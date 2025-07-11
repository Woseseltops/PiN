from django import template

register = template.Library()

@register.filter
def ce_year(value):

    if not isinstance(value, (int, str)):
        return value

    return str(abs(int(value))) + (" BCE" if int(value) < 0 else " CE")
