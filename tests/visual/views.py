"""The registry of admin views this package supports.

One list drives all three checks: the status test, the coverage guard and the
screenshot test. Adding an admin override means adding its view here.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from django.urls import reverse
from djangocms_versioning.helpers import version_list_url

from .data import VisualData


@dataclass(frozen=True)
class View:
    """One rendered page.

    ``url`` is a callable so entries read primary keys off the scenario instead of
    hardcoding them.
    """

    name: str
    url: Callable[[VisualData], str]
    status: int = 200
    auth: bool = True
    mask: tuple[str, ...] = field(default_factory=tuple)
    allowed_console_errors: tuple[str, ...] = field(default_factory=tuple)
    full_page: bool = True


VIEWS: tuple[View, ...] = (
    View(name="login", url=lambda data: reverse("admin:login"), auth=False),
    View(name="admin-index", url=lambda data: reverse("admin:index")),
    View(name="auth-user-changelist", url=lambda data: reverse("admin:auth_user_changelist")),
    View(name="auth-user-change", url=lambda data: reverse("admin:auth_user_change", args=[data.admin.pk])),
    View(name="auth-group-change", url=lambda data: reverse("admin:auth_group_add")),
    View(name="sites-site-change", url=lambda data: reverse("admin:sites_site_change", args=[1])),
    View(name="simplemodel-changelist", url=lambda data: reverse("admin:testapp_simplemodel_changelist")),
    View(name="simplemodel-add", url=lambda data: reverse("admin:testapp_simplemodel_add")),
    View(
        name="category-change-en",
        url=lambda data: reverse("admin:testapp_category_change", args=[data.category.pk]),
    ),
    View(
        name="category-change-de",
        url=lambda data: f"{reverse('admin:testapp_category_change', args=[data.category.pk])}?language=de",
    ),
    View(name="article-changelist", url=lambda data: reverse("admin:testapp_article_changelist")),
    View(
        name="document-change",
        url=lambda data: reverse("admin:testapp_document_change", args=[data.document.pk]),
    ),
    View(name="cms-pagetree", url=lambda data: reverse("admin:cms_pagecontent_changelist")),
    View(
        name="cms-pagecontent-change",
        url=lambda data: reverse("admin:cms_pagecontent_change", args=[data.page_content.pk]),
    ),
    View(name="versioning-versions", url=lambda data: version_list_url(data.page_content)),
    View(
        name="versioning-grouper",
        url=lambda data: reverse("admin:djangocms_versioning_pagecontentversion_grouper"),
    ),
    View(name="cms-usersettings", url=lambda data: reverse("admin:cms_usersettings_change")),
    View(name="filer-root", url=lambda data: reverse("admin:filer-directory_listing-root")),
    View(
        name="filer-folder-table",
        url=lambda data: reverse("admin:filer-directory_listing", args=[data.folder.pk]),
    ),
    View(
        name="filer-folder-thumbnails",
        # ``tb`` is filer's default list type; ``th`` is the thumbnail grid.
        url=lambda data: f"{reverse('admin:filer-directory_listing', args=[data.folder.pk])}?_list_type=th",
    ),
    View(
        name="filer-picker-popup",
        url=lambda data: (
            f"{reverse('admin:filer-directory_listing', args=[data.folder.pk])}?_pick=file&_popup=1"
        ),
    ),
    View(
        name="filer-make-folder",
        url=lambda data: (
            f"{reverse('admin:filer-directory_listing-make_folder', args=[data.folder.pk])}?_popup=1"
        ),
    ),
    View(name="filer-image-change", url=lambda data: reverse("admin:filer_image_change", args=[data.image.pk])),
    View(name="filer-file-change", url=lambda data: reverse("admin:filer_file_change", args=[data.file.pk])),
    View(name="filer-clipboard-changelist", url=lambda data: reverse("admin:filer_clipboard_changelist")),
    View(
        name="filer-thumbnailoption-changelist",
        url=lambda data: reverse("admin:filer_thumbnailoption_changelist"),
    ),
)
