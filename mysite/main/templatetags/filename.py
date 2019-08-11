from django.contrib.auth.models import Group
from django import template
import os

register = template.Library()


@register.filter
def filename(value):
    return os.path.basename(value.file.name)


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()



