from django import template

register = template.Library()

@register.filter(name='intdiv')
def intdiv(value, arg):
    """
    Integer division filter
    Returns the integer division of the value by the argument
    """
    try:
        return int(int(value) // int(arg))
    except (ValueError, TypeError):
        return 0

@register.filter(name='remainder')
def remainder(value, arg):
    """
    Remainder filter (modulo operation)
    Returns the remainder when value is divided by arg
    """
    try:
        return int(int(value) % int(arg))
    except (ValueError, TypeError):
        return 0
        
@register.filter(name='modulo')
def modulo(value, arg):
    """
    Modulo filter (alias for remainder)
    Returns the remainder when value is divided by arg
    """
    try:
        return int(int(value) % int(arg))
    except (ValueError, TypeError):
        return 0

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key
    Usage: {{ my_dict|get_item:my_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)