from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from unfold_extra.views import cms_set_language

urlpatterns = [
    path("i18n/setlang/", cms_set_language, name="set_language"),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("cms.urls")),
    prefix_default_language=False,
)
