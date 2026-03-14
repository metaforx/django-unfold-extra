from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from cms.plugin_pool import plugin_pool

from unfold_extra.contrib.cms.plugins import UnfoldCMSPluginBase, UnfoldStackedInline

from .models import HeroPluginModel, HeroButton


class HeroButtonInline(UnfoldStackedInline):
    model = HeroButton
    extra = 0


@plugin_pool.register_plugin
class HeroPlugin(UnfoldCMSPluginBase):
    model = HeroPluginModel
    name = _("Hero")
    render_template = "testapp/plugins/hero.html"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "subtitle",
                    "image",
                    "cta_label",
                    "cta_url",
                    "is_highlighted",
                    "layout",
                    "categories",
                )
            },
        ),
    )
    compressed_fields = True
    autocomplete_fields = ("categories",)
    #radio_fields = {"layout": admin.HORIZONTAL}
    readonly_fields = ("created_at",)
    inlines = (HeroButtonInline,)
