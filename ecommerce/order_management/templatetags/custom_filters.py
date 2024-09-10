from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiply value by arg and round to two decimal places."""
    try:
        result = float(value) * float(arg)
        return f"{result:.2f}"  # Format the result to two decimal places
    except (ValueError, TypeError):
        return "0.00"
    