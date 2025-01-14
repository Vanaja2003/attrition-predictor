from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        if value is None:
            return 0
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0  # Return 0 on error instead of empty string
