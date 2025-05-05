from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    if dictionary is None:
        return 0
    return dictionary.get(key, 0)

@register.filter(name='split')
def split(value, delimiter=','):
    if value is None:
        return []
    return value.split(delimiter)