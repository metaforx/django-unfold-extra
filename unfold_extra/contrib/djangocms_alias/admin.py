import djangocms_alias.admin  # noqa: F401  -- ensure stock alias admins register before our unregister/re-register

from cms.admin.utils import CONTENT_PREFIX
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.forms.widgets import HiddenInput

from djangocms_alias.admin import (
    AliasAdmin as BaseAliasAdmin,
)
from djangocms_alias.admin import (
    AliasContentAdmin as BaseAliasContentAdmin,
)
from djangocms_alias.admin import (
    CategoryAdmin as BaseCategoryAdmin,
)
from djangocms_alias.models import Alias, AliasContent, Category

from unfold.admin import ModelAdmin

from unfold_extra.contrib.parler.admin import UnfoldTranslatableAdminMixin

for model in (Alias, AliasContent, Category):
    if model in admin.site._registry:
        admin.site.unregister(model)


@admin.register(Category)
class CategoryAdmin(UnfoldTranslatableAdminMixin, BaseCategoryAdmin):
    pass


@admin.register(Alias)
class AliasAdmin(ModelAdmin, BaseAliasAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)
        # django-cms builds the synthetic ``content__*`` fields via ``modelform_factory``,
        # bypassing ``formfield_for_dbfield`` -- so they render unstyled. Restyle them
        # from ``formfield_overrides``; hidden grouping fields stay as-is.
        content_model = getattr(form_class, "_content_model", None)
        if content_model is None:
            return form_class
        for name in getattr(form_class, "_content_fields", ()):
            field = form_class.base_fields.get(CONTENT_PREFIX + name)
            if field is None or isinstance(field.widget, HiddenInput):
                continue
            try:
                db_field = content_model._meta.get_field(name)
            except FieldDoesNotExist:
                continue
            widget_cls = self._unfold_widget_for_dbfield(db_field)
            if widget_cls is not None and not isinstance(field.widget, widget_cls):
                field.widget = widget_cls(attrs=field.widget.attrs)
        return form_class

    def _unfold_widget_for_dbfield(self, db_field):
        """Walk ``formfield_overrides`` to find the correct Unfold widget.

        Overrides carrying a ``form_class`` are skipped — the widget alone won't fit.
        """
        for field_class in type(db_field).__mro__:
            override = self.formfield_overrides.get(field_class)
            if override and "widget" in override:
                if "form_class" in override:
                    return None
                return override["widget"]
        return None

    def get_actions_list(self, request=None):
        # Unfold's ``ActionModelAdminMixin`` (called with ``request``) and CMS's
        # ``GrouperModelAdmin`` (called without) clash here — dispatch on args.
        if request is None:
            return BaseAliasAdmin.get_actions_list(self)
        return ModelAdmin.get_actions_list(self, request)


@admin.register(AliasContent)
class AliasContentAdmin(ModelAdmin, BaseAliasContentAdmin):
    search_fields = ["name"]
