from cms.models.pluginmodel import CMSPlugin
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


# ---------------------------------------------------------------------------
# CMS Plugin models for testing UnfoldCMSPluginBase
# ---------------------------------------------------------------------------

class HeroPluginModel(CMSPlugin):
    """Hero section plugin exercising diverse field types."""

    LAYOUT_CHOICES = [
        ("centered", "Centered"),
        ("left", "Left-aligned"),
        ("right", "Right-aligned"),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    image = models.FileField(upload_to="hero/", blank=True)
    cta_label = models.CharField("CTA label", max_length=80, blank=True)
    cta_url = models.URLField("CTA URL", blank=True)
    is_highlighted = models.BooleanField(default=False)
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default="centered")
    categories = models.ManyToManyField(Category, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class HeroButton(models.Model):
    """Inline child for HeroPluginModel — tests UnfoldStackedInline."""

    hero = models.ForeignKey(
        HeroPluginModel, on_delete=models.CASCADE, related_name="buttons"
    )
    label = models.CharField(max_length=80)
    url = models.URLField()
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.label
