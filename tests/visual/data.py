"""Deterministic test data for the visual regression suite.

Builders follow the HackSoft styleguide's ``<entity>_create`` convention: keyword-only
arguments, full type hints, one object each. ``visual_data_create`` composes them into
the single scenario every registered view renders.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import datetime, timezone

from cms.api import create_page
from cms.models import Page, PageContent
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from djangocms_versioning.models import Version
from filer.models import File, Folder, Image
from PIL import Image as PILImage
from testapp.models import Article, Category, Document, SimpleModel

# Every ``auto_now*``, upload and version timestamp is pinned here, so repeated runs
# render identical dates. The value is timezone-aware because ``USE_TZ`` is on.
FIXED_TIMESTAMP = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def png_bytes(*, color: tuple[int, int, int], size: tuple[int, int] = (320, 200)) -> bytes:
    """A solid-colour PNG — fixed bytes for a fixed colour and size."""
    buffer = io.BytesIO()
    PILImage.new("RGB", size, color).save(buffer, "PNG")
    return buffer.getvalue()


def user_create(
    *,
    username: str,
    email: str,
    password: str = "visual-password",
    is_staff: bool = True,
    is_superuser: bool = False,
) -> User:
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )
    return user


def category_create(*, name_en: str, name_de: str, description_en: str = "", description_de: str = "") -> Category:
    category = Category.objects.language("en").create(name=name_en, description=description_en)
    category.create_translation("de", name=name_de, description=description_de)
    return category


def article_create(
    *,
    category: Category | None,
    title_en: str,
    title_de: str,
    body_en: str = "",
    body_de: str = "",
) -> Article:
    article = Article.objects.language("en").create(category=category, title=title_en, body=body_en)
    article.create_translation("de", title=title_de, body=body_de)
    return article


def simple_model_create(*, name: str, is_active: bool = True) -> SimpleModel:
    return SimpleModel.objects.create(name=name, is_active=is_active)


def filer_folder_create(*, owner: User, name: str, parent: Folder | None = None) -> Folder:
    return Folder.objects.create(name=name, owner=owner, parent=parent)


def filer_image_create(
    *,
    owner: User,
    folder: Folder | None,
    name: str,
    color: tuple[int, int, int],
) -> Image:
    filename = f"{name}.png"
    return Image.objects.create(
        owner=owner,
        folder=folder,
        name=name,
        original_filename=filename,
        file=SimpleUploadedFile(filename, png_bytes(color=color), content_type="image/png"),
    )


def filer_file_create(
    *,
    owner: User,
    folder: Folder | None,
    name: str,
    content: bytes = b"visual regression fixture\n",
) -> File:
    filename = f"{name}.txt"
    return File.objects.create(
        owner=owner,
        folder=folder,
        name=name,
        original_filename=filename,
        file=SimpleUploadedFile(filename, content, content_type="text/plain"),
    )


def document_create(*, title: str, file: File | None = None, cover: Image | None = None) -> Document:
    return Document.objects.create(title=title, file=file, cover=cover)


def cms_page_create(*, title: str, user: User, language: str = "en") -> PageContent:
    """A CMS page and its draft ``PageContent`` for ``language``.

    Goes through ``cms.api.create_page`` so djangocms-versioning builds the version
    graph the page tree and version list read.
    """
    page = create_page(title, "base.html", language, created_by=user)
    return page.get_admin_content(language)


@dataclass(frozen=True)
class VisualData:
    """The one scenario every registered view renders."""

    admin: User
    editor: User
    category: Category
    article: Article
    simple: SimpleModel
    folder: Folder
    subfolder: Folder
    image: Image
    file: File
    document: Document
    page_content: PageContent

    @property
    def page(self) -> Page:
        return self.page_content.page


def _timestamps_pin(*, data: VisualData) -> None:
    """Freeze every ``auto_now*`` field to ``FIXED_TIMESTAMP``.

    ``auto_now``/``auto_now_add`` overwrite whatever a builder passes on save, so the
    values are rewritten afterwards with ``update()``, which bypasses ``save()``.
    """
    User.objects.filter(pk__in=[data.admin.pk, data.editor.pk]).update(
        date_joined=FIXED_TIMESTAMP,
        last_login=FIXED_TIMESTAMP,
    )
    Folder.objects.filter(pk__in=[data.folder.pk, data.subfolder.pk]).update(
        uploaded_at=FIXED_TIMESTAMP,
        created_at=FIXED_TIMESTAMP,
        modified_at=FIXED_TIMESTAMP,
    )
    File.objects.filter(pk__in=[data.image.pk, data.file.pk]).update(
        uploaded_at=FIXED_TIMESTAMP,
        modified_at=FIXED_TIMESTAMP,
    )
    Article.objects.filter(pk=data.article.pk).update(created=FIXED_TIMESTAMP)
    Page.objects.filter(pk=data.page_content.page_id).update(
        creation_date=FIXED_TIMESTAMP,
        changed_date=FIXED_TIMESTAMP,
    )
    page_content_ids = list(
        PageContent.admin_manager.filter(page=data.page_content.page_id).values_list("pk", flat=True)
    )
    PageContent.admin_manager.filter(pk__in=page_content_ids).update(changed_date=FIXED_TIMESTAMP)
    Version.objects.filter(
        content_type=ContentType.objects.get_for_model(PageContent),
        object_id__in=page_content_ids,
    ).update(created=FIXED_TIMESTAMP, modified=FIXED_TIMESTAMP)

    for instance in (
        data.admin,
        data.editor,
        data.folder,
        data.subfolder,
        data.image,
        data.file,
        data.article,
        data.page_content,
    ):
        instance.refresh_from_db()


def visual_data_create(*, admin: User) -> VisualData:
    """Build the full scenario for ``admin`` and pin every timestamp it renders."""
    editor = user_create(username="editor", email="editor@example.com")

    category = category_create(
        name_en="Documentation",
        name_de="Dokumentation",
        description_en="Reference material.",
        description_de="Referenzmaterial.",
    )
    article = article_create(
        category=category,
        title_en="Release notes",
        title_de="Versionshinweise",
        body_en="What changed in this release.",
        body_de="Was sich in dieser Version geändert hat.",
    )
    simple = simple_model_create(name="Sample entry")

    folder = filer_folder_create(owner=admin, name="Assets")
    subfolder = filer_folder_create(owner=admin, name="Covers", parent=folder)
    image = filer_image_create(owner=admin, folder=subfolder, name="Cover", color=(38, 92, 164))
    file = filer_file_create(owner=admin, folder=folder, name="Handbook")

    document = document_create(title="Handbook 2026", file=file, cover=image)
    page_content = cms_page_create(title="Home", user=admin)

    data = VisualData(
        admin=admin,
        editor=editor,
        category=category,
        article=article,
        simple=simple,
        folder=folder,
        subfolder=subfolder,
        image=image,
        file=file,
        document=document,
        page_content=page_content,
    )
    _timestamps_pin(data=data)
    return data
