from django import template

register = template.Library()

@register.filter(name='format_phone_number')
def format_phone_number(phone_number):
    return "({}) {}-{}".format(phone_number[:3], phone_number[3:6], phone_number[6:])
