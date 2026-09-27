from django.contrib import admin
from djangocms_text.fields import HTMLField
from djangocms_text.widgets import TextEditorWidget
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin

from unfold_extra.contrib.parler.admin import (
    UnfoldTranslatableAdminMixin,
)

from .models import Article, Category, Document, Note, SimpleModel


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


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ["title"]


@admin.register(Note)
class NoteAdmin(ModelAdmin):
    list_display = ["title"]
    # Unfold's TextField override would otherwise replace the editor with a textarea
    formfield_overrides = {HTMLField: {"widget": TextEditorWidget}}

    def has_module_permission(self, request):
        # reached by URL only, so the sidebar in every visual reference stays unchanged
        return False
