import copy

from cms.models.fields import PageField
from cms.plugin_base import CMSPluginBase
from unfold.mixins.base_model_admin import BaseModelAdminMixin
from unfold.admin import StackedInline as UnfoldStackedInline
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.overrides import FORMFIELD_OVERRIDES

from unfold_extra.contrib.cms.widgets import UnfoldPageSelectWidget


class UnfoldCMSPluginBase(BaseModelAdminMixin, CMSPluginBase):
    """django CMS plugin base with Unfold admin form behavior and widget overrides."""

    formfield_overrides = {}

    #: Maps model-field classes → widget classes.  Applied post-construction
    #: in ``formfield_for_dbfield`` to work around fields that ignore the
    #: ``widget`` kwarg.  Subclasses can extend this dict.
    cms_widget_overrides = {
        PageField: UnfoldPageSelectWidget,
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


__all__ = [
    "UnfoldCMSPluginBase",
    "UnfoldStackedInline",
    "UnfoldTabularInline",
]
