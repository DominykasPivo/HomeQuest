from django import template

register = template.Library()

@register.filter
def filename(value):
    """Return only the filename from a path."""
    return value.split('/')[-1]