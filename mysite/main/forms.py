from django.contrib.auth.models import Group
from django import forms
from .models import Part, RFQ, Quote, Shipment
from .constants import PRIMARY_PROCESS_CHOICES, SECONDARY_PROCESS_CHOICES,THREE_AXIS_LASER,\
    FOUR_PLUS_AXIS_LASER, THREE_AXIS_WATERJET, FOUR_PLUS_AXIS_WATERJET, PLASMA, FORMING, PUNCHING,\
    TIMESAVE_SURFACE_FINISHING, VIBRATORY_DEBUR_AND_FINISHING, BEAD_BLASTING, POLISHING, MOST_INTERESTED_IN_CHOICES,\
    SHIPMENT_STATUS_CHOICES, INFORMATION_LABELS
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.mail import send_mail
from collections import OrderedDict


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    company = forms.CharField(max_length=50)
    title = forms.CharField(max_length=50)
    address = forms.CharField(max_length=100)
    address_2 = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=2)
    zip_code = forms.CharField(max_length=32)

    group = forms.ModelChoiceField(widget=forms.RadioSelect,
                                   required=True,
                                   empty_label=None,
                                   queryset=Group.objects.all().exclude(name__in=['Associate Admin', 'Admin']),
                                   initial='Buyer')

    processes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          required=False,
                                          choices=PRIMARY_PROCESS_CHOICES)

    secondary_processes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                    required=False,
                                                    choices=SECONDARY_PROCESS_CHOICES)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        #self.fields.pop('nickname')

        #merged_field_order = ['first_name', 'last_name', 'email', 'group', 'company', 'title', 'address', 'address_2','city', 'state', 'zip_code']

        #self.fields = OrderedDict(
            #(f, self.fields[f])
            #for f in merged_field_order)

    def signup(self, request, user):
        user.email = self.cleaned_data['email']
        user.save()

        group = self.cleaned_data['group']
        print(group)
        group = Group.objects.get(name=group)
        group.user_set.add(user)

        user.account.first_name = self.cleaned_data['first_name']
        user.account.last_name = self.cleaned_data['last_name']
        user.account.company = self.cleaned_data['company']
        user.account.title = self.cleaned_data['title']
        user.account.address = self.cleaned_data['address']
        user.account.address_2 = self.cleaned_data['address_2']
        user.account.city = self.cleaned_data['city']
        user.account.state = self.cleaned_data['state']
        user.account.zip_code = self.cleaned_data['zip_code']

        processes = self.cleaned_data['processes']
        secondary_processes = self.cleaned_data['secondary_processes']

        if group == Group.objects.get(name="Supplier"):
            user.account.three_axis_laser = False
            user.account.four_plus_axis_laser = False
            user.account.three_axis_waterjet = False
            user.account.four_plus_axis_waterjet = False
            user.account.plasma = False
            user.account.forming = False
            user.account.punching = False
            user.account.timesave_surface_finishing = False
            user.account.vibratory_debur_and_finishing = False
            user.account.bead_blasting = False
            user.account.polishing = False

            for p in processes:
                if p == THREE_AXIS_LASER:
                    user.account.three_axis_laser = True
                elif p == FOUR_PLUS_AXIS_LASER:
                    user.account.four_plus_axis_laser = True
                elif p == THREE_AXIS_WATERJET:
                    user.account.three_axis_waterjet = True
                elif p == FOUR_PLUS_AXIS_WATERJET:
                    user.account.four_plus_axis_waterjet = True
                elif p == PLASMA:
                    user.account.plasma = True

            for sp in secondary_processes:
                if sp == FORMING:
                    user.account.forming = True
                elif sp == PUNCHING:
                    user.account.punching = True
                elif sp == TIMESAVE_SURFACE_FINISHING:
                    user.account.timesave_surface_finishing = True
                elif sp == VIBRATORY_DEBUR_AND_FINISHING:
                    user.account.vibratory_debur_and_finishing = True
                elif sp == BEAD_BLASTING:
                    user.account.bead_blasting = True
                elif sp == POLISHING:
                    user.account.polishing = True

        user.account.save()


class CreatePartForm(forms.ModelForm):
    drawing = forms.FileField(required=True)
    cad_model = forms.FileField(required=True)

    class Meta:
        model = Part
        fields = ['name', 'number', 'material', 'material_thickness', 'process', 'drawing', 'cad_model']
        labels = {
            'material_thickness': 'Material Thickness (inch)',
            'cad_model': 'CAD model',
        }


class CreateRFQForm(forms.ModelForm):
    class Meta:
        model = RFQ
        fields = ['part', 'quantity', 'secondary_finishing_process', 'secondary_fabrication_process', 'zip_code',
                  'material_certification_required', 'inspection_type', 'notes', 'most_interested_in']

    def __init__(self, user, *args, **kwargs):
        super(CreateRFQForm, self).__init__(*args, **kwargs)
        self.fields['part'] = forms.ModelChoiceField(queryset=Part.objects.filter(user=user), empty_label=None,
                                                     required=True)
        self.fields['most_interested_in'] = forms.ChoiceField(widget=forms.RadioSelect,
                                                              required=True,
                                                              choices=MOST_INTERESTED_IN_CHOICES)


class AdminRFQForwardForm(forms.ModelForm):
    quote_by = forms.DateTimeField(initial=(datetime.now() + timedelta(days=1)))

    qs = User.objects.filter(groups__name='Supplier')
    supplier_1 = forms.ModelChoiceField(queryset=qs,
                                        required=True)
    supplier_2 = forms.ModelChoiceField(queryset=qs,
                                        required=False)
    supplier_3 = forms.ModelChoiceField(queryset=qs,
                                        required=False)

    class Meta:
        model = RFQ
        fields = ['supplier_1', 'supplier_2', 'supplier_3', 'quote_by']


class QuoteRFQForm(forms.ModelForm):
    acknowledgement = forms.BooleanField(required=True)

    class Meta:
        model = Quote
        fields = ['quantity', 'price_each', 'proposed_ship_date', 'estimated_package_weight', 'package_length',
                  'package_width', 'package_height', 'acknowledgement', 'notes']
        labels = {
            'estimated_package_weight': 'Estimated Package Weight (lbs)',
            'acknowledgement': 'I acknowledge this part/job specifications as described within the RFQ',
        }


class AdminQuoteAwardForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['marked_up_price_each', 'shipping_cost', 'estimated_receipt_date', 'sales_tax', 'total']


class BuyerShipInformationForm(forms.ModelForm):
    to_phone_number = forms.CharField(max_length=10, required=True)

    class Meta:
        model = Shipment
        fields = ['to_name', 'to_address', 'to_city', 'to_state', 'to_country', 'to_postal_code', 'to_phone_number']

        labels = INFORMATION_LABELS


class SupplierShipInformationForm(forms.ModelForm):
    from_phone_number = forms.CharField(max_length=10, required=True)

    class Meta:
        model = Shipment
        fields = ['from_name', 'from_address1', 'from_city', 'from_state', 'from_country', 'from_postal_code',
                  'from_phone_number']

        labels = INFORMATION_LABELS


class ShipmentStatusChangeForm(forms.ModelForm):
    status = forms.ChoiceField(widget=forms.RadioSelect,
                               choices=SHIPMENT_STATUS_CHOICES,
                               required=False)

    class Meta:
        model = Shipment
        fields = ['status']


class UpdatePartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'number', 'material', 'material_thickness', 'process', 'drawing', 'cad_model']


class ContactForm(forms.Form):
    name = forms.CharField(max_length=50)
    email = forms.EmailField()
    subject = forms.CharField(max_length=50)
    message = forms.CharField(widget=forms.Textarea)

    class Meta:
        fields = ['name', 'email', 'subject', 'message']

    def send_notification(self):
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['name'] + '\n' + self.cleaned_data['message']

        #send_mail(subject, message, self.cleaned_data['email'], ['mail@esourcelaser.com'])


