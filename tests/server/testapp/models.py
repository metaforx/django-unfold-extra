from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    """Translatable model for testing parler + unfold integration."""

    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        description=models.TextField(blank=True),
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or ""


class Article(TranslatableModel):
    """Translatable model with FK for testing parler admin + unfold."""

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)

    translations = TranslatedFields(
        title=models.CharField(max_length=200),
        body=models.TextField(blank=True),
    )

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or ""


class SimpleModel(models.Model):
    """Non-translatable model for basic unfold admin testing."""

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
