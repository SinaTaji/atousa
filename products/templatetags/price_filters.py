from django import template

register = template.Library()


@register.filter
def format_price(value):
    try:
        return "{:,} تومان ".format(int(value))
    except (ValueError, TypeError):
        return value
