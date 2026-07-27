from django.template import Library
from django.template.defaultfilters import capfirst
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from djangocms_alias.templatetags.djangocms_alias_tags import verbose_name

register = Library()

CELLS = "djangocms_alias/includes/cells/"


@register.simple_tag
def alias_usage_table(objects_list=None, hidden_usages=None):
    """Build the ``table`` payload for ``unfold/components/table.html``.

    Structure only — cell markup lives in the ``cells/`` partials. Both arguments
    come from ``get_alias_usage_context()`` and may be absent from the context.
    """
    rows = [
        [
            capfirst(verbose_name(item)),
            render_to_string(f"{CELLS}name.html", {"item": item}),
            render_to_string(f"{CELLS}usage.html", {"item": item}),
        ]
        for item in objects_list or []
    ]
    rows += [
        [
            capfirst(verbose_name(placeholder)),
            render_to_string(f"{CELLS}hidden_name.html", {"placeholder": placeholder}),
            "",
        ]
        for placeholder in hidden_usages or []
    ]
    return {"headers": [_("Type"), _("Name"), ""], "rows": rows}
