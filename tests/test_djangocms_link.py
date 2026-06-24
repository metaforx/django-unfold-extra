"""Tests for unfold_extra.contrib.djangocms_link.

Verify the stock djangocms-link plugin is swapped for an Unfold-styled variant
and that ``cms_widget_overrides`` applies Unfold widget styling to the fields
Unfold's automatic widget swapping cannot reach (the link MultiWidget and
attributes), while standard fields are styled by Unfold's overrides directly.
"""

from cms.plugin_pool import plugin_pool
from django.contrib import admin
from djangocms_attributes_field.fields import AttributesField
from djangocms_link.cms_plugins import LinkPlugin as StockLinkPlugin
from djangocms_link.fields import LinkField, LinkFormField
from djangocms_link.models import Link
from unfold.widgets import INPUT_CLASSES, SELECT_CLASSES

from unfold_extra.contrib.cms.plugins import UnfoldCMSPluginBase
from unfold_extra.contrib.djangocms_link.cms_plugins import LinkPlugin
from unfold_extra.contrib.djangocms_link.widgets import (
    UnfoldAttributesWidget,
    UnfoldLinkWidget,
)


def _plugin():
    plugin = plugin_pool.get_plugin("LinkPlugin")
    return plugin(plugin.model, admin.site)


def _formfield(field_name):
    """Build a field's admin formfield the way the change view does."""
    inst = _plugin()
    db_field = Link._meta.get_field(field_name)
    return inst.formfield_for_dbfield(db_field, request=None)


def test_link_plugin_is_swapped():
    """The registered Link plugin is our Unfold subclass."""
    plugin = plugin_pool.get_plugin("LinkPlugin")
    assert issubclass(plugin, LinkPlugin)
    assert issubclass(plugin, UnfoldCMSPluginBase)


def test_plugin_keeps_link_display_name():
    """The plugin must show as 'Link', not the humanized UnfoldCMSPluginBase name."""
    plugin = plugin_pool.get_plugin("LinkPlugin")
    assert str(plugin.name) == str(StockLinkPlugin.name)
    assert "CMSPlugin" not in str(plugin.name)


def test_plugin_type_name_preserved():
    """plugin_type must stay 'LinkPlugin' so existing DB instances still resolve."""
    assert LinkPlugin.__name__ == "LinkPlugin"
    assert "LinkPlugin" in plugin_pool.plugins
    assert "UnfoldLinkPlugin" not in plugin_pool.plugins


def test_widget_overrides_registered():
    """The plugin extends the base overrides with link/attributes widgets."""
    overrides = LinkPlugin.cms_widget_overrides
    assert overrides[LinkField] is UnfoldLinkWidget
    assert overrides[AttributesField] is UnfoldAttributesWidget
    # Base overrides (e.g. PageField) are preserved, not replaced.
    assert overrides.items() >= UnfoldCMSPluginBase.cms_widget_overrides.items()


def test_standard_fields_styled_without_a_form():
    """name/target/template get Unfold widgets from the override alone."""
    assert "Unfold" in type(_formfield("name").widget).__name__
    for key in ("target", "template"):
        assert "Unfold" in type(_formfield(key).widget).__name__


def test_link_field_keeps_styled_multiwidget():
    """Override restores djangocms-link's MultiWidget over Unfold's Textarea swap.

    djangocms-link's prepare_value/to_python access widget.widgets, so the link
    field must remain a (styled) MultiWidget after formfield_for_dbfield runs.
    """
    formfield = _formfield("link")
    assert isinstance(formfield, LinkFormField), "link parsing logic lost"
    widget = formfield.widget
    assert isinstance(widget, UnfoldLinkWidget)
    assert hasattr(widget, "widgets")
    styled = [
        w
        for w in widget.widgets
        if SELECT_CLASSES[0] in w.attrs.get("class", "")
        or INPUT_CLASSES[0] in w.attrs.get("class", "")
    ]
    assert styled, "no link sub-widget received Unfold classes"


def test_link_field_roundtrips_through_styled_widget():
    """Swapping the widget must not break djangocms-link's value parsing."""
    formfield = _formfield("link")
    value = formfield.widget.value_from_datadict(
        {"link_0": "external_link", "link_1": "https://example.com"}, {}, "link"
    )
    assert formfield.to_python(value) == {"external_link": "https://example.com"}


def test_attributes_field_inputs_are_styled():
    """attributes key/value inputs carry Unfold classes (render ignores attrs)."""
    formfield = _formfield("attributes")
    assert isinstance(formfield.widget, UnfoldAttributesWidget)
    html = formfield.widget.render("attributes", {"rel": "nofollow"})
    assert " ".join(INPUT_CLASSES) in html
