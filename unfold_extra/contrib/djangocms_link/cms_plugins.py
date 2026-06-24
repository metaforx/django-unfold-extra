from cms.plugin_pool import plugin_pool
from djangocms_attributes_field.fields import AttributesField
from djangocms_link.cms_plugins import LinkPlugin as StockLinkPlugin
from djangocms_link.fields import LinkField
from unfold_extra.contrib.cms.plugins import UnfoldCMSPluginBase

from unfold_extra.contrib.djangocms_link.widgets import (
    UnfoldAttributesWidget,
    UnfoldLinkWidget,
)

plugin_pool.unregister_plugin(StockLinkPlugin)

@plugin_pool.register_plugin
class LinkPlugin(UnfoldCMSPluginBase, StockLinkPlugin):
    name = StockLinkPlugin.name
    module = StockLinkPlugin.module
    cms_widget_overrides = {
        **UnfoldCMSPluginBase.cms_widget_overrides,
        LinkField: UnfoldLinkWidget,
        AttributesField: UnfoldAttributesWidget,
    }
