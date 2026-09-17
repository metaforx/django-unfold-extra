from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from unfold_extra.views import cms_set_language


def serve_media(request, path):
    """Serve uploads under ``live_server``, which runs with DEBUG off.

    ``MEDIA_ROOT`` is redirected per test, so it is read on each request rather than
    bound at import time.
    """
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve_media),
    path("i18n/setlang/", cms_set_language, name="set_language"),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("cms.urls")),
    prefix_default_language=False,
)
