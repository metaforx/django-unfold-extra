import copy

from cms.models.fields import PageField
from cms.plugin_base import CMSPluginBase
from django import forms
from django.contrib.admin.widgets import (
    AdminTextareaWidget,
    AdminTextInputWidget,
    RelatedFieldWidgetWrapper,
)
from unfold import widgets as unfold_widgets
from unfold.admin import StackedInline as UnfoldStackedInline
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.mixins import (
    ActionModelAdminMixin,
    DatasetModelAdminMixin,
    FormFieldModelAdminMixin,
    NestedInlinesModelAdminMixin,
)
from unfold.overrides import FORMFIELD_OVERRIDES

from unfold_extra.contrib.cms.widgets import UnfoldPageSelectWidget


# unfold >=0.92 split BaseModelAdminMixin into these four mixins; keep
# ModelAdmin's order, with CMSPluginBase in place of Django's BaseModelAdmin.
class UnfoldCMSPluginBase(
    FormFieldModelAdminMixin,
    ActionModelAdminMixin,
    DatasetModelAdminMixin,
    NestedInlinesModelAdminMixin,
    CMSPluginBase,
):
    """django CMS plugin base with Unfold admin form behavior and widget overrides."""

    formfield_overrides = {}

    # DatasetModelAdminMixin.changeform_view() calls get_changeform_datasets(),
    # which Unfold's own ModelAdmin provides directly (not via the mixin itself).
    # Since CMSPluginBase stands in for Unfold's BaseModelAdmin here, replicate it.
    change_form_datasets = ()

    def get_changeform_datasets(self, request):
        return self.change_form_datasets

    #: Maps model-field classes → widget classes.  Applied post-construction
    #: in ``formfield_for_dbfield`` to work around fields that ignore the
    #: ``widget`` kwarg.  Subclasses can extend this dict.
    cms_widget_overrides = {
        PageField: UnfoldPageSelectWidget,
    }

    #: Maps stock widget classes → Unfold equivalents, for fields declared on the
    #: form (``formfield_overrides`` only reaches model-derived ones). Matched on
    #: exact type, so a plugin's own widget subclass is never swapped out.
    unfold_form_widget_overrides = {
        forms.TextInput: unfold_widgets.UnfoldAdminTextInputWidget,
        AdminTextInputWidget: unfold_widgets.UnfoldAdminTextInputWidget,
        forms.Textarea: unfold_widgets.UnfoldAdminTextareaWidget,
        AdminTextareaWidget: unfold_widgets.UnfoldAdminTextareaWidget,
        forms.CheckboxInput: unfold_widgets.UnfoldBooleanWidget,
        forms.Select: unfold_widgets.UnfoldAdminSelectWidget,
        forms.SelectMultiple: unfold_widgets.UnfoldAdminSelectMultipleWidget,
    }

    def __init__(self, model=None, admin_site=None):
        # Allow django CMS to call plugin() with no args.
        overrides = copy.deepcopy(FORMFIELD_OVERRIDES)
        for k, v in self.formfield_overrides.items():
            overrides.setdefault(k, {}).update(v)
        self.formfield_overrides = overrides

        super().__init__(model, admin_site)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None:
            for field_cls, widget_cls in self.cms_widget_overrides.items():
                if isinstance(db_field, field_cls):
                    formfield.widget = widget_cls()
                    break
        return formfield

    def render_change_form(self, request, context, *args, **kwargs):
        # Fields declared on the form never reach formfield_for_dbfield, and views
        # that build their own form (djangocms_alias' "Create Alias") have none.
        form = getattr(context.get("adminform"), "form", None)
        for field in getattr(form, "fields", {}).values():
            self.apply_unfold_widget(field)
        return super().render_change_form(request, context, *args, **kwargs)

    def apply_unfold_widget(self, field):
        """Restyle one form field with its Unfold equivalent, in place."""
        widget = field.widget
        if isinstance(widget, RelatedFieldWidgetWrapper):
            widget.template_name = "unfold/widgets/related_widget_wrapper.html"
            return
        replacement = self.unfold_form_widget_overrides.get(type(widget))
        if replacement is None:
            return
        field.widget = replacement(attrs=dict(widget.attrs))
        if hasattr(widget, "choices"):
            field.widget.choices = widget.choices


# CMSPluginBaseMetaclass stamps a derived ``name`` and a generated ``form`` onto every
# subclass -- including this base. Sitting first in a plugin's MRO, they would shadow
# the real plugin's values, so drop them and let lookups fall through.
del UnfoldCMSPluginBase.name
del UnfoldCMSPluginBase.form


__all__ = [
    "UnfoldCMSPluginBase",
    "UnfoldStackedInline",
    "UnfoldTabularInline",
]
