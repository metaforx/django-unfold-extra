import filer.admin  # noqa: F401  -- ensure stock filer admin registers before our unregister/re-register
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from filer.admin.clipboardadmin import ClipboardAdmin as FilerClipboardAdmin
from filer.admin.fileadmin import FileAdmin as FilerFileAdmin
from filer.admin.fileadmin import FileAdminChangeFrom as FilerFileAdminForm
from filer.admin.folderadmin import FolderAdmin as FilerFolderAdmin
from filer.admin.imageadmin import ImageAdmin as FilerImageAdmin
from filer.admin.imageadmin import ImageAdminForm as FilerImageAdminForm
from filer.admin.permissionadmin import PermissionAdmin as FilerPermissionAdmin
from filer.admin.thumbnailoptionadmin import (
    ThumbnailOptionAdmin as FilerThumbnailOptionAdmin,
)
from filer.models import Clipboard, File, Folder, FolderPermission, ThumbnailOption
from filer.settings import FILER_IMAGE_MODEL
from filer.utils.loader import load_model
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminImageFieldWidget

Image = load_model(FILER_IMAGE_MODEL)


class _UnfoldFilerFileWidgetMixin:
    """Give filer's ``file`` field an Unfold-styled upload control.

    filer's ``FileAdminChangeFrom.__init__`` hard-sets ``forms.FileInput()`` on
    the instance's ``file`` field, which bypasses Unfold's ``FORMFIELD_OVERRIDES``
    and renders as a bare, unstyled ``<input type="file">``. We re-apply Unfold's
    widget *after* filer's ``__init__`` has run (a ``get_form`` override is too
    early — filer overwrites the widget again at instantiation).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "file" in self.fields:
            self.fields["file"].widget = UnfoldAdminImageFieldWidget()


class UnfoldFileAdminForm(_UnfoldFilerFileWidgetMixin, FilerFileAdminForm):
    pass


class UnfoldImageAdminForm(_UnfoldFilerFileWidgetMixin, FilerImageAdminForm):
    pass


class _FilerCanonicalLinkMixin:
    """Render the read-only canonical URL as a visible Unfold-styled link.

    filer's ``display_canonical`` returns a bare ``<a>`` that is visually
    indistinct from plain text under Unfold. We re-render it with Unfold's link
    classes so it clearly reads (and behaves) as a link.
    """

    @admin.display(description=_("canonical URL"))
    def display_canonical(self, instance):
        canonical = instance.canonical_url
        if canonical:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer"'
                ' class="text-primary-600 hover:underline dark:text-primary-500">{}</a>',
                canonical,
                canonical,
            )
        return "—"


for model in (Folder, File, Clipboard, Image, FolderPermission, ThumbnailOption):
    if model in admin.site._registry:
        admin.site.unregister(model)


# Unfold's ModelAdmin must come first in the MRO, so its templates, media and
# context win over filer's stock admin (mirrors contrib.cms.PageContentAdmin,
# which is declared as ``class PageContentAdmin(ModelAdmin, BasePageContentAdmin)``).
@admin.register(Folder)
class FolderAdmin(ModelAdmin, FilerFolderAdmin):
    # The directory listing is not a model changelist, so Unfold's header ends up
    # without a breadcrumb. Point filer at our subclassed template, which swaps in
    # an Unfold-styled header. It cannot live at filer's own template path the way
    # admin_filer.css shadows filer's static path — it *extends* filer's template,
    # so shadowing would make it extend itself. filer ships two listings that
    # differ only in block names, so mirror whichever one it picked.
    directory_listing_template = (
        "unfold_extra/filer/folder/legacy_listing.html"
        if FilerFolderAdmin.directory_listing_template.endswith("legacy_listing.html")
        else "unfold_extra/filer/folder/directory_listing.html"
    )


@admin.register(File)
class FileAdmin(_FilerCanonicalLinkMixin, ModelAdmin, FilerFileAdmin):
    form = UnfoldFileAdminForm


@admin.register(Clipboard)
class ClipboardAdmin(ModelAdmin, FilerClipboardAdmin):
    pass


@admin.register(Image)
class ImageAdmin(_FilerCanonicalLinkMixin, ModelAdmin, FilerImageAdmin):
    form = UnfoldImageAdminForm


@admin.register(FolderPermission)
class PermissionAdmin(ModelAdmin, FilerPermissionAdmin):
    pass


@admin.register(ThumbnailOption)
class ThumbnailOptionAdmin(ModelAdmin, FilerThumbnailOptionAdmin):
    pass
