from django.apps import apps
from django.conf import settings
from django.utils.translation import activate, check_for_language
from django.views.i18n import LANGUAGE_QUERY_PARAMETER, set_language


def cms_set_language(request):
    """Set Django's language and keep CMS ``UserSettings.language`` in sync."""
    param = getattr(settings, "LANGUAGE_QUERY_PARAMETER", LANGUAGE_QUERY_PARAMETER)
    raw_language = request.POST.get(param, request.GET.get(param))
    language = raw_language if raw_language and check_for_language(raw_language) else None

    if raw_language and param != LANGUAGE_QUERY_PARAMETER:
        if request.method == "POST" and param in request.POST:
            post = request.POST.copy()
            post[LANGUAGE_QUERY_PARAMETER] = raw_language
            request._post = post
        elif param in request.GET:
            query = request.GET.copy()
            query[LANGUAGE_QUERY_PARAMETER] = raw_language
            request._get = query

    if (
        language
        and getattr(request, "user", None)
        and request.user.is_staff
        and apps.is_installed("cms")
    ):
        from cms.models import UserSettings

        UserSettings.objects.update_or_create(
            user=request.user,
            defaults={"language": language},
        )

    # Keep the source language active so Django can translate the referer URL.
    cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    if cookie_lang and check_for_language(cookie_lang):
        activate(cookie_lang)

    response = set_language(request)

    # Make sure middleware writes the target language back to the cookie.
    if language:
        activate(language)

    return response
