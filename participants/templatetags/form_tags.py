from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Añade una clase CSS a un widget de formulario.
    """
    return value.as_widget(attrs={'class': arg})