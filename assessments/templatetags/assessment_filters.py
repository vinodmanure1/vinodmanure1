from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Template filter to get item from dictionary."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def stringformat(value, format_str):
    """Format a value as string."""
    return format_str % value
