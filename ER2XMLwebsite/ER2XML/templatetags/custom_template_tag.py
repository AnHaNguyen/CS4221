from django import template

register = template.Library()

@register.assignment_tag
def get_item(dictionary, key):
    return dictionary.get(key)