from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def percentage(value, total):
    try:
        return f"{(value / total * 100):.1f}%"
    except ZeroDivisionError:
        return "0%"

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.simple_tag
def active_page(request, view_name):
    if request.resolver_match.view_name == view_name:
        return 'active'
    return ''