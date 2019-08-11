# primary processes
THREE_AXIS_LASER = "3 Axis Laser"
FOUR_PLUS_AXIS_LASER = "4+ Axis Laser"
THREE_AXIS_WATERJET = "3 Axis Waterjet"
FOUR_PLUS_AXIS_WATERJET = "4+ Axis Waterjet"
PLASMA = "Plasma"


PRIMARY_PROCESS_CHOICES = (
    (THREE_AXIS_LASER, "3 Axis Laser"),
    (FOUR_PLUS_AXIS_LASER, "4+ Axis Laser"),
    (THREE_AXIS_WATERJET, "3 Axis Waterjet"),
    (FOUR_PLUS_AXIS_WATERJET, "4+ Axis Waterjet"),
    (PLASMA, "Plasma")
)

# secondary processes
FORMING = "Forming"
PUNCHING = "punching"
TIMESAVE_SURFACE_FINISHING = "Timesave Surface Finishing"
VIBRATORY_DEBUR_AND_FINISHING = "Vibratory Debur & Finishing"
BEAD_BLASTING = "Bead Blasting"
POLISHING = "Polishing"

SECONDARY_PROCESS_CHOICES = (
    (FORMING, "Forming"),
    (PUNCHING, "Punching"),
    (TIMESAVE_SURFACE_FINISHING, "Timesave Surface Finishing"),
    (VIBRATORY_DEBUR_AND_FINISHING, "Vibratory Debur and Finishing"),
    (BEAD_BLASTING, "Bead Blasting"),
    (POLISHING, "Polishing")
)

# material thicknesses
ONE = "1.0000"

MATERIAL_THICKNESS_CHOICES = (
    (ONE, "1.0000"),
    ("0.7500", "0.7500"),
    ("0.6250", "0.6250"),
    ("0.5000", "0.5000"),
    ("0.4688", "0.4688"),
    ("0.4375", "0.4375"),
    ("0.4063", "0.4063"),
    ("0.3750", "0.3750"),
    ("0.3438", "0.3438"),
    ("0.3125", "0.3125"),
    ("0.2813", "0.2813"),
    ("0.2656", "0.2656"),
    ("0.2500", "0.2500"),
    ("0.2344", "0.2344"),
    ("0.2188", "0.2188"),
    ("0.2031", "0.2031"),
    ("0.1875", "0.1875"),
    ("0.1719", "0.1719"),
    ("0.1563", "0.1563"),
    ("0.1406", "0.1406"),
    ("0.1250", "0.1250"),
    ("0.1094", "0.1094"),
    ("0.0938", "0.0938"),
    ("0.0781", "0.0781"),
    ("0.0703", "0.0703"),
    ("0.0625", "0.0625"),
    ("0.0563", "0.0563"),
    ("0.0500", "0.0500"),
    ("0.0438", "0.0438"),
    ("0.0375", "0.0375"),
    ("0.0344", "0.0344"),
    ("0.0313", "0.0313"),
    ("0.0281", "0.0281"),
    ("0.0250", "0.0250"),
    ("0.0219", "0.0219"),
    ("0.0188", "0.0188"),
    ("0.0172", "0.0172"),
    ("0.0156", "0.0156"),
    ("0.0141", "0.0141"),
    ("0.0125", "0.0125"),
    ("0.0109", "0.0109"),
    ("0.0102", "0.0102"),
    ("0.0094", "0.0094"),
    ("0.0086", "0.0086"),
    ("0.0078", "0.0078"),
    ("0.0070", "0.0070"),
    ("0.0066", "0.0066"),
    ("0.0063", "0.0063")
)

# secondary processes (finishing)
NOTHING = "None (No Cost)"
TIMESAVE_SURFACE_A = "Timesave Surface - A"
TIMESAVE_SURFACE_B = "Timesave Surface - Both Sides"

SECONDARY_FINISHING_PROCESS_CHOICES = (
    (NOTHING, "None (No Cost)"),
    (TIMESAVE_SURFACE_A, "Timesave Surface - A"),
    (TIMESAVE_SURFACE_B, "Timesave Surface - Both Sides"),
    (VIBRATORY_DEBUR_AND_FINISHING, "Vibratory Debur & Finishing"),
    (BEAD_BLASTING, "Bead Blasting"),
    (POLISHING, "Polishing")
)

# secondary processes (fabrication)
FORMING_PER_DRAWING = "Forming Per Drawing"
PUNCHING_PER_DRAWING = "Punching Per Drawing"

SECONDARY_FABRICATION_PROCESS_CHOICES = (
    (NOTHING, "None (No Cost)"),
    (FORMING_PER_DRAWING, "Forming Per Drawing"),
    (PUNCHING_PER_DRAWING, "Punching Per Drawing")
)

# inspection types
STANDARD = "Standard (No Cost)"
EACH_PIECE = "Each Piece (Documented)"
FIRST_ARTICLE = "First Article (Documented)"

INSPECTION_TYPE_CHOICES = (
    (STANDARD, "Standard (No Cost)"),
    (EACH_PIECE, "Each Piece (Documented)"),
    (FIRST_ARTICLE, "First Article (Documented)")
)

# most interested in
PRICE = "Price"
LEAD_TIME = "Lead Time"

MOST_INTERESTED_IN_CHOICES = (
    (PRICE, "Price"),
    (LEAD_TIME, "Lead Time")
)

# shipping
UNKNOWN = "Unknown"
NOT_SHIPPED = "Started - Not Shipped"
SHIPPED = "Shipped"
PENDING = "Pending - Not started"


SHIPMENT_STATUS_CHOICES = (
    (PENDING, "Pending - Not started"),
    (NOT_SHIPPED, "Started - Not Shipped"),
    (SHIPPED, "Shipped"),
)

# information labels
INFORMATION_LABELS = {
    'from_name': 'Name',
    'from_address': 'Address',
    'from_city': 'City',
    'from_state': 'State',
    'from_country': 'Country',
    'from_postal_code': 'Postal Code',
    'from_phone_number': 'Phone Number',
}


