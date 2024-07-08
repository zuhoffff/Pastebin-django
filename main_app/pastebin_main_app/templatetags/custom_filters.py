from django import template

register = template.Library()

@register.filter(name='replace_underscore')
def replace_underscores(value):
    return value.replace('_', ' ')