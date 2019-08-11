from ClassicUPS import UPSConnection
from.file_paths import content_shipping_label_file_name
import os

LICENSE_NUMBER = ''
USER_ID = ''
PASSWORD = ''
SHIPPER_NUMBER = ''


def ship(shipment):

    ups = UPSConnection(LICENSE_NUMBER,
                        USER_ID,
                        PASSWORD,
                        SHIPPER_NUMBER,  # Optional if you are not creating a shipment
                        debug=True)  # Use the UPS sandbox API rather than prod

    from_addr = {
        'name': shipment.from_name,
        'address1': shipment.from_address1,
        'city': shipment.from_city,
        'state': shipment.from_state,
        'country': shipment.from_country,
        'postal_code': shipment.from_postal_code,
        'phone': shipment.from_phone_number
    }
    to_addr = {
        'name': shipment.to_name,
        'address1': shipment.to_address,
        'city': shipment.to_city,
        'state': shipment.to_state,
        'country': shipment.to_country,
        'postal_code': shipment.to_postal_code,
        'phone': shipment.to_phone_number
    }
    dimensions = {  # in inches
        'length': shipment.quote.package_length,
        'width': shipment.quote.package_width,
        'height': shipment.quote.package_height
    }
    weight = shipment.quote.estimated_package_weight  # in lbs

    # Create the shipment. Use file_format='EPL' for a thermal-printer-compatible EPL
    s = ups .create_shipment(from_addr, to_addr, dimensions, weight, file_format='GIF')

    path = content_shipping_label_file_name(shipment, '')

    if not os.path.exists(path):
        os.makedirs(path)

    path += 'label.gif'

    s.save_label(open(path, 'w+b'))

    shipment.tracking_number = s.tracking_number
    shipment.cost = str(s.cost)
    shipment.label = path
    shipment.ups_connection = ups
    shipment.save()


def track(shipment):
    ups = UPSConnection(LICENSE_NUMBER,
                        USER_ID,
                        PASSWORD,
                        debug=True)  # Use the UPS sandbox API rather than prod

    tracking = ups.tracking_info('')

    print(tracking)

    return tracking
