from django.conf import settings
from django.utils.translation import activate, check_for_language
from django.views.i18n import set_language


def cms_set_language(request):
    """Drop-in replacement for Django's ``set_language`` view that also
    updates the CMS ``UserSettings.language`` field.

    CMS's ``ToolbarMiddleware`` reads ``UserSettings.language`` to determine
    the admin toolbar language. ``LanguageCookieMiddleware`` overwrites the
    language cookie from ``get_language()`` on every response unless the
    request cookie already matches.

    We update ``UserSettings`` before calling Django's ``set_language``
    so that both the cookie and the DB agree when the next request arrives.

    Unfold's language form sends ``next=""`` (the template's
    ``{{ redirect_to }}`` is unset in admin context). Django's
    ``set_language`` handles this correctly by falling back to
    ``HTTP_REFERER`` and using ``translate_url()`` to convert the referer
    to the target language, but only when ``translate_url`` can
    ``resolve()`` the source URL, which requires the source language to be
    active.

    When ``prefix_default_language=False`` is used in ``i18n_patterns``,
    ``LocaleMiddleware`` forces ``LANGUAGE_CODE`` for all URLs without a
    language prefix, including this endpoint. We re-activate the language
    from the cookie so that ``translate_url`` can resolve the referer URL.

    Wire this up in ``urls.py``::

        from unfold_extra.views import cms_set_language

        urlpatterns = [
            path("i18n/setlang/", cms_set_language, name="set_language"),
            path("i18n/", include("django.conf.urls.i18n")),
            ...
        ]
    """
    language = request.POST.get("language", request.GET.get("language"))

    # Update (or create) CMS UserSettings before the redirect.
    # ``update_or_create`` ensures this works even for users who have never
    # visited the CMS user-settings page (no existing row).
    if language and getattr(request, "user", None) and request.user.is_staff:
        try:
            from cms.models import UserSettings

            UserSettings.objects.update_or_create(
                user=request.user,
                defaults={"language": language},
            )
        except Exception:
            pass

    # Re-activate the user's current language from the cookie.
    # LocaleMiddleware forces settings.LANGUAGE_CODE for non-prefixed URLs
    # when prefix_default_language=False. ``translate_url()`` inside
    # ``set_language()`` needs the source language active to resolve() the
    # referer/next URL correctly.
    cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    if cookie_lang and check_for_language(cookie_lang):
        activate(cookie_lang)

    response = set_language(request)

    # Activate the target language so that CMS's LanguageCookieMiddleware
    # writes the correct cookie value when it processes the response.
    if language:
        activate(language)

    return response
