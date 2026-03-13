from django.contrib import admin
from unfold.admin import ModelAdmin

from unfold_extra.contrib.parler.admin import (
    UnfoldTranslatableAdminMixin,
)
from parler.admin import TranslatableAdmin

from .models import Article, Category, SimpleModel


@admin.register(Category)
class CategoryAdmin(UnfoldTranslatableAdminMixin, TranslatableAdmin, ModelAdmin):
    list_display = ["name"]
    search_fields = ["translations__name"]


@admin.register(Article)
class ArticleAdmin(UnfoldTranslatableAdminMixin, TranslatableAdmin, ModelAdmin):
    list_display = ["title", "category", "created"]
    list_filter = ["category"]
    search_fields = ["translations__title"]


@admin.register(SimpleModel)
class SimpleModelAdmin(ModelAdmin):
    list_display = ["name", "is_active"]
    search_fields = ["name"]
