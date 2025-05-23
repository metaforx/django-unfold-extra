from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def unfold_extra_styles(context):
    if context.get('user') and context['user'].is_authenticated:
        return mark_safe(f'<link rel="stylesheet" type="text/css" href="{static("unfold/css/styles.css")}">')
    return ''
