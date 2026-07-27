import djangocms_alias.cms_plugins  # noqa: F401  -- stock plugin must register before we swap it

from cms.plugin_pool import plugin_pool
from djangocms_alias.cms_plugins import Alias as BaseAliasPlugin
from djangocms_alias.forms import AliasPluginForm

from unfold_extra.contrib.cms.plugins import UnfoldCMSPluginBase

# ``category`` and ``alias`` are declared on the form, so ``formfield_overrides``
# never sees them. Unfold's select2 CSS only targets the ``admin-autocomplete``
# theme, which select2 picks up from this attribute -- see unfold.widgets.
SELECT2_ATTRS = {
    "data-theme": "admin-autocomplete",
    "class": "unfold-admin-autocomplete admin-autocomplete",
}
SELECT2_FIELDS = ("category", "alias")


class UnfoldAliasPluginForm(AliasPluginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in SELECT2_FIELDS:
            field = self.fields.get(name)
            if field is None:
                continue
            attrs = field.widget.attrs
            attrs["data-theme"] = SELECT2_ATTRS["data-theme"]
            attrs["class"] = " ".join(
                filter(None, [attrs.get("class"), SELECT2_ATTRS["class"]])
            )


# Unregister whoever holds the slot, not just the stock class, so a re-import
# swaps cleanly instead of raising PluginAlreadyRegistered.
if (registered := plugin_pool.plugins.get(BaseAliasPlugin.__name__)) is not None:
    plugin_pool.unregister_plugin(registered)


# Keep the class name: existing plugin instances are stored as ``plugin_type="Alias"``.
@plugin_pool.register_plugin
class Alias(UnfoldCMSPluginBase, BaseAliasPlugin):
    form = UnfoldAliasPluginForm
