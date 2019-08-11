from djmoney.models.fields import MoneyField
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from .file_paths import content_part_file_name, content_shipping_label_file_name
from .constants import PRIMARY_PROCESS_CHOICES, THREE_AXIS_LASER, MATERIAL_THICKNESS_CHOICES, ONE,\
    SECONDARY_FINISHING_PROCESS_CHOICES, NOTHING, SECONDARY_FABRICATION_PROCESS_CHOICES, INSPECTION_TYPE_CHOICES,\
    STANDARD, SHIPMENT_STATUS_CHOICES, UNKNOWN
from pinax.stripe.actions.customers import create
from pinax.stripe.models import Charge
from ClassicUPS import UPSConnection


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    company = models.CharField(max_length=50, default='')
    title = models.CharField(max_length=50, default='')
    address = models.CharField(max_length=100, default='')
    address_2 = models.CharField(max_length=100, default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=50, default='')
    zip_code = models.CharField(max_length=32, default='')
    three_axis_laser = models.NullBooleanField(blank=True, default=None)
    four_plus_axis_laser = models.NullBooleanField(blank=True, default=None)
    three_axis_waterjet = models.NullBooleanField(blank=True, default=None)
    four_plus_axis_waterjet = models.NullBooleanField(blank=True, default=None)
    plasma = models.NullBooleanField(blank=True, default=None)
    forming = models.NullBooleanField(blank=True, default=None)
    punching = models.NullBooleanField(blank=True, default=None)
    timesave_surface_finishing = models.NullBooleanField(blank=True, default=None)
    vibratory_debur_and_finishing = models.NullBooleanField(blank=True, default=None)
    bead_blasting = models.NullBooleanField(blank=True, default=None)
    polishing = models.NullBooleanField(blank=True, default=None)

    def __str__(self):
        return self.user.email


def create_account(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        account = Account(user=user)
        account.save()

        # stripe customer
        create(user, charge_immediately=False)

post_save.connect(create_account, sender=User)


class Part(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='part_user')
    name = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    upload_date = models.DateTimeField()
    material = models.CharField(max_length=50)
    material_thickness = models.CharField(max_length=10, choices=MATERIAL_THICKNESS_CHOICES, default=ONE)
    process = models.CharField(max_length=50, choices=PRIMARY_PROCESS_CHOICES, default=THREE_AXIS_LASER)
    drawing = models.FileField(upload_to=content_part_file_name)
    cad_model = models.FileField(upload_to=content_part_file_name)

    def __str__(self):
        return str(self.name) + ' - ' + str(self.number)


class RFQ(models.Model):
    # entered at first creation
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rfq_user')
    part = models.ForeignKey(Part, related_name='rfq_part')
    quantity = models.CharField(max_length=50, blank=False)
    secondary_finishing_process = models.CharField(max_length=30, choices=SECONDARY_FINISHING_PROCESS_CHOICES, default=NOTHING, blank=False)
    secondary_fabrication_process = models.CharField(max_length=30, choices=SECONDARY_FABRICATION_PROCESS_CHOICES, default=NOTHING, blank=False)
    zip_code = models.CharField(max_length=25, blank=False)
    material_certification_required = models.BooleanField()
    inspection_type = models.CharField(max_length=30, choices=INSPECTION_TYPE_CHOICES, default=STANDARD, blank=False)
    notes = models.TextField(max_length=500)
    most_interested_in = models.CharField(max_length=30, blank=False)
    # entered by admin after initial creation
    is_open = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    quote_by = models.DateTimeField(null=True, blank=True)
    supplier_1 = models.ForeignKey(User, related_name='rfq_supplier_1', null=True, blank=True)
    supplier_2 = models.ForeignKey(User, related_name='rfq_supplier_2', null=True, blank=True)
    supplier_3 = models.ForeignKey(User, related_name='rfq_supplier_3', null=True, blank=True)
    charge = models.ForeignKey(Charge, null=True, blank=True)


class Quote(models.Model):
    # entered at first creation
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quote_user')
    rfq = models.ForeignKey(RFQ, related_name='quote_rfq')
    quantity = models.IntegerField(blank=False)
    price_each = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    proposed_ship_date = models.DateField(blank=False)
    estimated_package_weight = models.DecimalField(max_digits=5, decimal_places=1)
    package_length = models.IntegerField()
    package_width = models.IntegerField()
    package_height = models.IntegerField()
    acknowledgement = models.BooleanField(default=False)
    notes = models.TextField(max_length=500)
    # entered by admin after initial creation
    marked_up_price_each = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    shipping_cost = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    estimated_receipt_date = models.DateField(null=True, blank=True)
    sales_tax = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    total = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    active = models.BooleanField(default=False)
    awarded = models.NullBooleanField(blank=True, default=None)
    needs_payment = models.NullBooleanField(blank=True, default=None)


class Shipment(models.Model):
    rfq = models.ForeignKey(RFQ, related_name='shipment_rfq', null=True, blank=True)
    quote = models.ForeignKey(Quote, related_name='shipment_quote', null=True, blank=True)
    # to
    to_name = models.CharField(max_length=50)
    to_address = models.CharField(max_length=50)
    to_city = models.CharField(max_length=50)
    to_state = models.CharField(max_length=2)
    to_country = models.CharField(max_length=2)
    to_postal_code = models.CharField(max_length=10)
    # from
    from_name = models.CharField(max_length=50)
    from_address1 = models.CharField(max_length=50)
    from_city = models.CharField(max_length=50)
    from_state = models.CharField(max_length=2)
    from_country = models.CharField(max_length=2)
    from_postal_code = models.CharField(max_length=10)
    # status stuff
    status = models.CharField(max_length=50, choices=SHIPMENT_STATUS_CHOICES, default=UNKNOWN)
    last_status_change_time = models.DateTimeField(null=True, blank=True)
    to_phone_number = models.CharField(max_length=10, null=True, blank=True)
    from_phone_number = models.CharField(max_length=10, null=True, blank=True)
    tracking_number = models.CharField(max_length=50, null=True, blank=True)
    cost = models.CharField(max_length=20, null=True, blank=True)
    label = models.FileField(null=True, blank=True)



