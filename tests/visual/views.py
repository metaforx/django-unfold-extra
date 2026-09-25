"""The registry of admin views this package supports.

One list drives all three checks: the status test, the coverage guard and the
screenshot test. Adding an admin override means adding its view here.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from cms.toolbar.utils import get_object_edit_url, get_object_structure_url
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
    # Runs after the page settles, for views that only exist after an interaction.
    setup: Callable[[object, VisualData], None] | None = None


# filer renders the action form with Unfold's widgets, whose x-model="action" and
# x-model="selectAcross" expect a changelist Alpine scope filer's page never declares.
# Documented in CLAUDE.md as cosmetic: the form still submits.
FILER_ALPINE_ERRORS = ("action is not defined", "selectAcross is not defined")

def _page_settings_modal_open(page, data: VisualData) -> None:
    """Open the toolbar's Page > Page settings... modal and wait for its iframe."""
    page_menu = page.locator(".cms-toolbar-item-navigation > li").filter(
        has=page.locator("> a", has_text=re.compile(r"^\s*Page\s*$"))
    )
    page_menu.locator("> a").click()
    page_menu.locator("ul a").filter(has_text="Page settings").click()
    page.wait_for_selector(".cms-modal", state="visible")
    page.frame_locator(".cms-modal iframe").locator("#content").wait_for(state="visible")
    page.wait_for_load_state("networkidle")


def _plugin_edit_modal_open(page, data: VisualData) -> None:
    """Double-click the hero plugin, the way an editor opens it, and wait for the modal."""
    page.locator(f".cms-plugin-{data.hero_plugin.pk}").first.dblclick()
    page.wait_for_selector(".cms-modal", state="visible")
    page.frame_locator(".cms-modal iframe").locator("#content").wait_for(state="visible")
    page.wait_for_load_state("networkidle")


VIEWS: tuple[View, ...] = (
    View(name="login", url=lambda data: reverse("admin:login"), auth=False),
    View(name="admin-index", url=lambda data: reverse("admin:index")),
    View(name="auth-user-changelist", url=lambda data: reverse("admin:auth_user_changelist")),
    View(name="auth-user-change", url=lambda data: reverse("admin:auth_user_change", args=[data.editor.pk])),
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
    View(
        name="cms-frontend-edit",
        url=lambda data: get_object_edit_url(data.page_content, language="en"),
    ),
    View(
        name="cms-frontend-structure",
        url=lambda data: get_object_structure_url(data.page_content, language="en"),
    ),
    View(
        name="cms-page-settings-modal",
        url=lambda data: get_object_edit_url(data.page_content, language="en"),
        # The modal is viewport chrome; a full-page capture would stretch it.
        full_page=False,
        setup=_page_settings_modal_open,
    ),
    View(
        name="cms-plugin-edit-modal",
        url=lambda data: get_object_edit_url(data.page_content, language="en"),
        full_page=False,
        setup=_plugin_edit_modal_open,
    ),
    View(name="filer-root", url=lambda data: reverse("admin:filer-directory_listing-root"), allowed_console_errors=FILER_ALPINE_ERRORS),
    View(
        name="filer-folder-table",
        url=lambda data: reverse("admin:filer-directory_listing", args=[data.folder.pk]),
        allowed_console_errors=FILER_ALPINE_ERRORS,
    ),
    View(
        name="filer-folder-thumbnails",
        # ``tb`` is filer's default list type; ``th`` is the thumbnail grid.
        url=lambda data: f"{reverse('admin:filer-directory_listing', args=[data.folder.pk])}?_list_type=th",
        allowed_console_errors=FILER_ALPINE_ERRORS,
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
    View(
        name="filer-clipboard-changelist",
        url=lambda data: reverse("admin:filer_clipboard_changelist"),
        allowed_console_errors=FILER_ALPINE_ERRORS,
    ),
    View(
        name="filer-thumbnailoption-changelist",
        url=lambda data: reverse("admin:filer_thumbnailoption_changelist"),
        allowed_console_errors=FILER_ALPINE_ERRORS,
    ),
)
