from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from braces.views import GroupRequiredMixin
from django.views.generic import View
from .forms import CreatePartForm, CreateRFQForm, AdminRFQForwardForm, QuoteRFQForm, AdminQuoteAwardForm,\
    BuyerShipInformationForm, SupplierShipInformationForm, ShipmentStatusChangeForm, UpdatePartForm, ContactForm
from datetime import datetime
from .models import Part, RFQ, Quote, Shipment, Account
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from .permissions import group_required
from .pay import charge
from .constants import UNKNOWN, PENDING
from .ship import ship, track
from itertools import chain
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Class views

class HomepageView(SuccessMessageMixin, View):
    form_class = ContactForm
    success_message = "Successfully sent"

    def dispatch(self, request, *args, **kwargs):
        return super(HomepageView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class(request.GET)
        return render(request, "main/unauthenticated_homepage.html", {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        messages.success(request, "Successfully sent")

        if form.is_valid():
            form.send_notification()
            return redirect('/')

        return render(request, "main/unauthenticated_homepage.html", {'form': form})


class CreatePartView(GroupRequiredMixin, View):
    group_required = [u"Buyer"]
    redirect_field_name = '/error/'

    form_class = CreatePartForm
    template_name = 'main/create_part.html'

    def get(self, request):
        form = self.form_class(None)

        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            i = form.save(commit=False)
            i.user = request.user
            i.upload_date = datetime.now()
            i.save()

            return redirect('/part/' + str(i.id) + '/')

        return render(request, self.template_name, {'form': form})


class CreateRFQView(GroupRequiredMixin, View):
    group_required = [u"Buyer"]
    redirect_field_name = '/error/'

    form_class = CreateRFQForm
    template_name = 'main/create_rfq.html'

    def get(self, request):

        form = self.form_class(User.objects.get(username=request.user.username))

        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(User.objects.get(username=request.user.username), request.POST)

        if form.is_valid():
            i = form.save(commit=False)
            i.user = request.user
            i.save()

            return redirect('/rfq/' + str(i.id) + '/')

        return render(request, self.template_name, {'form': form})


# Function Views

@group_required('Buyer')
def part_detail_view(request, pk):
    part = get_object_or_404(Part, pk=pk)
    open_rfqs = RFQ.objects.filter(part=part).filter(is_open=True)

    if not(request.user == part.user):
        raise Http404("You're not allowed to access this part.")

    if len(open_rfqs) > 0:
        edit_allowed = False
    else:
        edit_allowed = True

    context = {
        'part': part,
        'edit_allowed': edit_allowed,
    }

    return render(request, 'main/part_detail.html', context)


def edit_part_view(request, pk):
    part = get_object_or_404(Part, id=pk)

    if not request.user.username == part.user.username:
        raise Http404

    if request.method == "POST":
        if not RFQ.objects.filter(part=part, is_open=True):
            form = UpdatePartForm(request.POST, request.FILES, instance=part)

            if form.is_valid():
                form.save()
        else:
            messages.add_message(request, messages.ERROR, 'You have open RFQs for this part. Close them to edit.')

        return redirect('/part/' + str(part.id) + '/')

    else:
        form = UpdatePartForm(instance=part)

    context = {
        'form': form,
    }

    return render(request, "main/edit_part.html", context)


def error_view(request):
    return render(request, "main/error.html")


@group_required('Buyer', 'Supplier', 'Associate Admin')
def rfq_detail_view(request, pk):
    rfq = get_object_or_404(RFQ, pk=pk)

    if request.user.groups.filter(name__in=['Buyer']):
        if not(request.user.username == rfq.user.username):
            raise Http404("You can't access this RFQ")
    elif request.user.groups.filter(name__in=['Supplier']):
        if not(request.user == rfq.supplier_1)\
                and not(request.user == rfq.supplier_2) \
                and not(request.user == rfq.supplier_3):
            raise Http404("You can't access this RFQ")
    elif request.user.groups.filter(name__in=['Associate Admin']):
        pass

    if request.method == "POST":
        #print(request.POST.get('close'))
        if request.POST.get('close') is None:
            form = AdminRFQForwardForm(request.POST, instance=rfq)

            if form.is_valid():
                i = form.save(commit=False)

                # this is very convoluted, should be looked into more
                if form.cleaned_data['supplier_1'] is not None:
                    i.supplier_1 = User.objects.get(username=form.cleaned_data['supplier_1'])
                    if form.cleaned_data['supplier_2'] is not None:
                        i.supplier_2 = User.objects.get(username=form.cleaned_data['supplier_2'])
                        if form.cleaned_data['supplier_1'].username == form.cleaned_data['supplier_2'].username:
                            messages.add_message(request, messages.ERROR, 'You cannot add a supplier more than once!')
                            return render(request, 'main/rfq_detail.html', {'form': form, 'rfq': rfq})

                        if form.cleaned_data['supplier_3'] is not None:
                            i.supplier_3 = User.objects.get(username=form.cleaned_data['supplier_3'])
                            if form.cleaned_data['supplier_1'].username == form.cleaned_data['supplier_3'].username \
                                    or form.cleaned_data['supplier_2'].username == form.cleaned_data[
                                        'supplier_3'].username:
                                messages.add_message(request, messages.ERROR,
                                                     'You cannot add a supplier more than once!')
                                return render(request, 'main/rfq_detail.html', {'form': form, 'rfq': rfq})
                else:
                    messages.add_message(request, messages.ERROR, 'You must add a supplier!')
                    return render(request, 'main/rfq_detail.html', {'form': form, 'rfq': rfq})

                if i.is_open:
                    i.is_open = False
                    i.is_pending = True
                else:
                    i.is_open = True
                    i.is_pending = False
                i.save()

                subject = render_to_string("main/new_RFQ_email_subject.html")
                message = render_to_string("main/new_RFQ_email_body.html", {'rfq': rfq})

                print(message)

                #if i.supplier_1 is not None:
                    # send_mail(subject, message, i.supplier_1.email, 'admin@esourcelaser.com')
                #if i.supplier_2 is not None:
                    # send_mail(subject, message, i.supplier_2.email, 'admin@esourcelaser.com')
                #if i.supplier_3 is not None:
                    # send_mail(subject, message, i.supplier_3.email, 'admin@esourcelaser.com')

            return render(request, 'main/rfq_detail.html', {'form': form, 'rfq': rfq})
        else:
            rfq.is_open = False
            rfq.is_pending = True
            rfq.save()
            return redirect('/rfq/' + str(rfq.id) + '/')

    else:
        form = AdminRFQForwardForm(instance=rfq)
        return render(request, 'main/rfq_detail.html', {'form': form, 'rfq': rfq})


@group_required('Associate Admin')
def admin_view(request):
    rfqs = RFQ.objects.all().order_by('-id')
    quotes = Quote.objects.all()
    accounts = Account.objects.all()

    context = {
        'rfqs': rfqs,
        'quotes': quotes,
        'accounts': accounts,
    }

    return render(request, "main/administration.html", context)


@group_required('Supplier', 'Associate Admin')
def quote_rfq_view(request, pk):
    rfq = get_object_or_404(RFQ, pk=pk)

    quote = Quote.objects.filter(user=request.user).filter(rfq=rfq)

    if request.method == "POST":
        form = QuoteRFQForm(request.POST)
        if form.is_valid():
            i = form.save(commit=False)
            i.user = request.user
            i.rfq = rfq
            i.save()

            return redirect('/supplier/')
    else:
        form = QuoteRFQForm(None)

    context = {
        'rfq': rfq,
        'quote': quote,
        'form': form,
    }

    return render(request, "main/quote_rfq.html", context)


@group_required('Supplier', 'Associate Admin', 'Buyer')
def quote_detail_view(request, pk):
    quote = get_object_or_404(Quote, pk=pk)

    if not(request.user == quote.user) \
            and not(request.user.groups.filter(name__in=['Associate Admin'])) \
            and not(request.user == quote.rfq.user):
        raise Http404("You can't access that quote")

    if request.user.groups.filter(name__in=['Buyer']).exists():
        if not buyer_allowed(request, quote):
            raise Http404("Buyers can only access awarded quotes")

    if request.method == "POST":
        form = AdminQuoteAwardForm(request.POST, instance=quote)

        if form.is_valid():
            i = form.save(commit=False)

            if 'with_award' in request.POST:

                if form.cleaned_data['estimated_receipt_date'] < quote.proposed_ship_date:
                    messages.add_message(request, messages.ERROR, 'The receive date cannot be before the ship date.')
                    return render(request, "main/quote_detail.html", {'form': form, 'quote': quote})

                i.active = True
                i.awarded = True
                i.needs_payment = True

                other_quotes = Quote.objects.filter(rfq=quote.rfq)
                for q in other_quotes:
                    q.awarded = False
                    q.save()

            i.save()
            return redirect('/administration/')

    else:
        form = AdminQuoteAwardForm(instance=quote)
        shipment = Shipment.objects.filter(quote=quote)
        if shipment:
            shipment = shipment[0]

    context = {
        'form': form,
        'quote': quote,
        'shipment': shipment,
    }

    return render(request, "main/quote_detail.html", context)


def buyer_allowed(request, quote):
    if request.user == quote.rfq.user and quote.awarded and quote.active:
        return True
    return False


def buyer_payment_view(request, pk):
    rfq = get_object_or_404(RFQ, pk=pk)

    quote = Quote.objects.filter(rfq=rfq, awarded=True, active=True)[0]

    if quote is None:
        raise Http404("You can't pay for a rfq that has no quotes")

    if not quote.needs_payment:
        raise Http404("This quote was already payed for")

    if request.method == "POST":
        form = BuyerShipInformationForm(request.POST)
        if form.is_valid():

            try:
                charge(request, quote, request.POST.get('stripeToken'))
            except Exception:
                messages.error(request, "There was an error with the payment.")
                return redirect('/buyer/' + str(rfq.id) + '/pay')

            quote.needs_payment = False
            quote.save()

            rfq.is_open = False
            rfq.save()

            i = form.save(commit=False)
            i.rfq = rfq
            i.quote = quote
            i.status = UNKNOWN
            i.last_status_change_time = datetime.now()
            i.save()

            subject = render_to_string("main/new_charge_email_subject")
            message = render_to_string("main/new_charge_email_body", {'quote': quote})

            # send_mail(subject, message, ['admin@esourcelaser.com', quote.user.email], 'admin@esourcelaser.com')

            return redirect('/buyer/')

    form = BuyerShipInformationForm()
    shipment = Shipment.objects.filter(rfq=rfq, quote=quote)
    context = {
        'rfq': rfq,
        'quote': quote,
        'form': form,
        'shipment': shipment,
    }

    return render(request, 'main/buyer_payment.html', context)


@group_required('Buyer')
def buyer_home_view(request):
    rfqs = RFQ.objects.filter(user=request.user).order_by('-id')
    quotes = Quote.objects.all()
    parts = Part.objects.filter(user=request.user).order_by('-id')

    context = {
        'rfqs': rfqs,
        'quotes': quotes,
        'parts': parts,
    }

    return render(request, 'main/buyer.html', context)


@group_required('Supplier')
def supplier_home_view(request):
    rfqs_1 = RFQ.objects.filter(supplier_1=request.user)
    rfqs_2 = RFQ.objects.filter(supplier_2=request.user)
    rfqs_3 = RFQ.objects.filter(supplier_3=request.user)

    rfqs = list(chain(rfqs_1, rfqs_2, rfqs_3))

    quotes = Quote.objects.filter(user=request.user)

    return render(request, "main/supplier.html", {'rfqs': rfqs, 'quotes': quotes})


def shipment_view(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)

    if request.method == "POST":

        if shipment.status == UNKNOWN:
            form = SupplierShipInformationForm(request.POST, instance=shipment)

            if form.is_valid():
                i = form.save(commit=False)
                i.status = PENDING
                i.last_status_change_time = datetime.now()
                print(shipment.quote)
                i.save()

                ship(shipment)

        else:
            form = ShipmentStatusChangeForm(request.POST, instance=shipment)

            if form.is_valid():
                i = form.save(commit=False)
                i.last_status_change_time = datetime.now()
                i.save()

    else:

        if shipment.status == UNKNOWN:
            form = SupplierShipInformationForm(instance=shipment)
        else:
            form = ShipmentStatusChangeForm(instance=shipment)

    return render(request, "main/shipment.html", {'shipment': shipment, 'form': form})


def home(request):
    if request.user.groups.filter(name__in=['Buyer']):
        return redirect('/buyer/')

    elif request.user.groups.filter(name__in=['Supplier']):
        return redirect('/supplier/')

    elif request.user.groups.filter(name__in=['Associate Admin']):
        return redirect('/administration/')

    return redirect('/')


def faq_view(request):
    return render(request, "main/faq.html", {})


def supplier_faq_view(request):
    return render(request, "main/sup_faq.html", {})
