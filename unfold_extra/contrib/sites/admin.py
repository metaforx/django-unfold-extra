from django.contrib import admin
from django.contrib.sites.models import Site

from unfold.admin import ModelAdmin

if Site in admin.site._registry:
    admin.site.unregister(Site)


@admin.register(Site)
class SiteAdmin(ModelAdmin):
    search_fields = ["domain", "name"]
