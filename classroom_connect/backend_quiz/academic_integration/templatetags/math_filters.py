from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return None
        
@register.filter
def intdiv(value, arg):
    """Integer division of the value by the argument"""
    try:
        return int(float(value) // float(arg))
    except (ValueError, TypeError, ZeroDivisionError):
        return None
        
@register.filter
def modulo(value, arg):
    """Return the remainder when value is divided by arg"""
    try:
        return int(int(value) % int(arg))
    except (ValueError, TypeError, ZeroDivisionError):
        return None
        
@register.filter
def remainder(value, arg):
    """Alias for modulo filter"""
    try:
        return int(int(value) % int(arg))
    except (ValueError, TypeError, ZeroDivisionError):
        return None