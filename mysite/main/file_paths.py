from datetime import datetime


def content_part_file_name(instance, filename):
    now = datetime.now()
    return '/'.join(['content', instance.user.username, 'parts', instance.name+'-'+instance.number,
                     now.strftime('%b_%d_%I_%M_%p'), filename])


def content_shipping_label_file_name(instance, filename):
    now = datetime.now()
    return '/'.join(['media', 'content', 'shipping_labels', instance.rfq.part.name + '-' + str(instance.id),
                     now.strftime('%b_%d_%I_%M_%p'), filename])
