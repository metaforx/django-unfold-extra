from parler.admin import (
    TranslatableStackedInline as BaseTranslatableStackedInline,
)
from parler.admin import (
    TranslatableTabularInline as BaseTranslatableTabularInline,
)
from unfold.admin import ModelAdmin, StackedInline, TabularInline

from .forms import UnfoldTranslatableModelForm


class UnfoldTranslatableAdminMixin(ModelAdmin):
    form = UnfoldTranslatableModelForm


class UnfoldTranslatableStackedAdminMixin(StackedInline):
    form = UnfoldTranslatableModelForm


class UnfoldTranslatableTabularAdminMixin(TabularInline):
    form = UnfoldTranslatableModelForm


class TranslatableStackedInline(
    UnfoldTranslatableStackedAdminMixin, BaseTranslatableStackedInline
):
    pass


class TranslatableTabularInline(
    UnfoldTranslatableTabularAdminMixin, BaseTranslatableTabularInline
):
    pass
