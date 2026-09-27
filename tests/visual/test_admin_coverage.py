"""No admin registration slips into the package without a rendering decision.

Every model on the default admin site either has its changelist in the registry, or an
explicit entry in ``EXCLUDED`` saying why it isn't worth a reference image.
"""

from __future__ import annotations

import pytest
from django.contrib import admin
from django.urls import resolve

from .views import VIEWS

# label -> why the changelist has no registry entry
EXCLUDED: dict[str, str] = {
    "auth.group": "the add form is registered instead, for the permission filter widget",
    "cms.page": "hidden from the index (has_module_permission is False); the tree is cms.pagecontent",
    "cms.placeholder": "no user-facing changelist; placeholders are edited on the page",
    "cms.usersettings": "singleton change view, registered as cms-usersettings",
    "djangocms_link.link": "plugin model, edited in the CMS plugin modal (deferred)",
    "filer.file": "filer replaces the changelist with its directory listing",
    "filer.folder": "filer replaces the changelist with its directory listing",
    "filer.folderpermission": "plain Unfold changelist, no unfold_extra override",
    "filer.image": "filer replaces the changelist with its directory listing",
    "sites.site": "the change form is registered instead; the changelist holds one row",
    "testapp.category": "test-app model; both change form languages are registered",
    "testapp.document": "test-app model; the change form carries the filer widgets",
}


def _covered_url_names(*, data) -> set[str]:
    return {resolve(view.url(data).split("?")[0]).url_name for view in VIEWS}


@pytest.mark.django_db
def test_every_registered_model_is_covered_or_excluded(visual_data):
    covered = _covered_url_names(data=visual_data)

    missing = []
    for model in admin.site._registry:
        label = f"{model._meta.app_label}.{model._meta.model_name}"
        changelist = f"{model._meta.app_label}_{model._meta.model_name}_changelist"
        if changelist in covered or label in EXCLUDED:
            continue
        missing.append(label)

    assert not missing, (
        "registered models with no registry entry and no EXCLUDED reason: "
        + ", ".join(sorted(missing))
    )


def test_excluded_entries_state_a_reason():
    empty = [label for label, reason in EXCLUDED.items() if not reason.strip()]
    assert not empty, f"EXCLUDED entries need a reason: {', '.join(sorted(empty))}"
