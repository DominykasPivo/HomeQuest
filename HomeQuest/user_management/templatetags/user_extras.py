from django import template

register = template.Library()

@register.filter
def is_instance(user, class_name):
    return user.__class__.__name__ == class_name