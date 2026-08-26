from django import template
from django.template import RequestContext
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from filer.admin.tools import admin_url_params_encoded

register = template.Library()


def _label(obj) -> str:
    """filer's display name: ``label`` on File/Image, ``name`` everywhere else."""
    return getattr(obj, "label", None) or obj.name


@register.simple_tag(takes_context=True)
def filer_breadcrumb_parts(context: RequestContext, obj) -> list[dict]:
    """Unfold ``header_title`` parts for any filer object with a ``logical_path``."""
    params = admin_url_params_encoded(context["request"])

    parts = [
        {"link": reverse("admin:app_list", args=["filer"]), "title": _("Filer")},
        {
            "link": reverse("admin:filer-directory_listing-root") + params,
            "title": _("Folder"),
        },
    ]

    for ancestor in getattr(obj, "logical_path", None) or []:
        parts.append(
            {
                "link": ancestor.get_admin_directory_listing_url_path() + params,
                "title": _label(ancestor),
            }
        )

    # The root pseudo-folder is already the "Folder" crumb; smart folders are not.
    if not getattr(obj, "is_root", False) or getattr(obj, "is_smart_folder", False):
        parts.append({"title": _label(obj)})

    return parts
