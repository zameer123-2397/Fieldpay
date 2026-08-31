from django import template
from invoices.currencies import get_symbol

register = template.Library()


@register.filter
def currency_symbol(code):
    return get_symbol(code)