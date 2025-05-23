from django.contrib import admin
from django.contrib.sites.models import Site

from unfold.admin import ModelAdmin

admin.site.unregister(Site)


@admin.register(Site)
class SiteAdmin(ModelAdmin):
    pass
