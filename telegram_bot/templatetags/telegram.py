from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='t_link')
@stringfilter
def t_link(value):
    if '@' in value:
        link = 'https://t.me/{}'.format(str(value))
        a_tag = '<a href="{link}" >{value}</a>'.format(link=link, value=value)
        return a_tag
    return value
