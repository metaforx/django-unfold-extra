import copy

from cms.plugin_base import CMSPluginBase
from unfold.mixins.base_model_admin import BaseModelAdminMixin
from unfold.admin import StackedInline as UnfoldStackedInline
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.overrides import FORMFIELD_OVERRIDES


class UnfoldCMSPluginBase(BaseModelAdminMixin,CMSPluginBase):
    """
    django CMS plugin base with Unfold form behavior.

    Accepts django CMS's no-args init path.
    """

    formfield_overrides = {}

    def __init__(self, model=None, admin_site=None):
        # Allow django CMS to call plugin() with no args.
        overrides = copy.deepcopy(FORMFIELD_OVERRIDES)
        for k, v in self.formfield_overrides.items():
            overrides.setdefault(k, {}).update(v)
        self.formfield_overrides = overrides

        super().__init__(model, admin_site)


__all__ = [
    "UnfoldCMSPluginBase",
    "UnfoldStackedInline",
    "UnfoldTabularInline",
]
