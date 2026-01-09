from django import template
from finance.utils import convert_amount

register = template.Library()

@register.filter
def currency_convert(value, arg):
    """
    Converts amount to user's currency (User object) or specific currency code.
    Usage: {{ amount|currency_convert:user }} OR {{ amount|currency_convert:"USD" }}
    """
    target_currency = 'USD'
    
    if hasattr(arg, 'currency'):
        target_currency = arg.currency
    elif arg:
        target_currency = str(arg)
    
    # Check if value is None or empty
    if value is None:
        return 0.0
        
    return convert_amount(value, target_currency)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
