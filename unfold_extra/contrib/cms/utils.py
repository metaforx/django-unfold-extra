from cms.admin.pageadmin import get_site
from cms.constants import MODAL_HTML_REDIRECT
from cms.utils.conf import get_cms_setting
from cms.utils.i18n import get_site_language_from_request
from django.http import HttpResponse
from django.urls import reverse
from urllib.parse import urlencode
from json import dumps

from django.utils.text import capfirst
from django.utils.translation import gettext

SIDEPANEL_HTML_REDIRECT = """<!doctype html>
<meta http-equiv="refresh" content="0;url={url}">
<script>window.location.replace({url_json});</script>
<a href="{url}">Redirecting…</a>
"""

def _request_is_iframe(request) -> bool:
    """
    Determines if the request is intended for an iframe.

    This function inspects the request headers to check if the "Sec-Fetch-Dest"
    header is present and its value is set to "iframe".
    """
    return request.headers.get("Sec-Fetch-Dest") == "iframe"

def _request_is_toolbar_modal(request) -> bool:
    """
    Determines if the current request is related to a CMS toolbar modal.
    """
    if request.POST.get("_cms_modal") == "1":
        return True
    if "cms_path" in request.GET:
        return True
    ref = (request.META.get("HTTP_REFERER") or "").lower()
    return "cms_path=" in ref


def _language_from_request(request) -> str:
    """
    Determines the language to be used based on the request object.
    """
    site = get_site(request)
    lang = request.GET.get("language") or get_site_language_from_request(request, site_id=site.pk)
    return lang or get_cms_setting("LANGUAGE_CODE")

def _sidepanel_return_url(request, url) -> str:
    """
    Build the admin PageContent changelist URL and preserve existing query parameters
    from the current request, excluding internal admin flags.
    """
    params = request.GET.copy()
    for excluded_param in ["_popup", "_to_field", "_changelist_filters"]:
        params.pop(excluded_param, None)
    return f"{url}?{urlencode(params, doseq=True)}" if params else url

def _html_modal_redirect(url) -> HttpResponse:
    """
    Redirects to a given URL using an HTML modal.
    """
    return HttpResponse(MODAL_HTML_REDIRECT.format(url=url, url_json=dumps(url)))

def _html_sidepanel_redirect(url) -> HttpResponse:
    """
    Redirects to a URL via an HTML sidepanel.
    """
    return HttpResponse(SIDEPANEL_HTML_REDIRECT.format(url=url, url_json=dumps(url)))


def _admin_add_success_message(obj) -> str:
    """
    Build a translatable success message for an added object.
    """
    return gettext('%(name)s "%(obj)s" was added successfully.') % {
        "name": capfirst(obj._meta.verbose_name),
        "obj": obj,
    }

def _admin_change_success_message(obj) -> str:
    """
    Generate a success message for an admin object when it has been successfully changed.
    """
    return gettext('%(name)s "%(obj)s" was changed successfully.') % {
        "name": capfirst(obj._meta.verbose_name),
        "obj": obj,
    }

def _admin_delete_success_message(obj) -> str:
    return gettext('"%(obj)s" was deleted successfully.') % {
        "obj": obj,
    }