"""The rendering scenario must be byte-identical on every run.

Screenshot comparison only means something when the data behind it never moves: the
same primary keys, names and timestamps, so a diff is always a rendering change.
"""

from __future__ import annotations

import pytest

from .data import VisualData, visual_data_create

FINGERPRINTS: list[dict[str, object]] = []


def _fingerprint(data: VisualData) -> dict[str, object]:
    return {
        "admin": (data.admin.pk, data.admin.username, data.admin.last_login, data.admin.date_joined),
        "editor": (data.editor.pk, data.editor.username, data.editor.last_login),
        "category": (data.category.pk, str(data.category)),
        "article": (data.article.pk, str(data.article), data.article.created),
        "simple": (data.simple.pk, data.simple.name),
        "folder": (data.folder.pk, data.folder.name, data.folder.created_at, data.folder.modified_at),
        "subfolder": (data.subfolder.pk, data.subfolder.name, data.subfolder.created_at),
        "image": (data.image.pk, data.image.name, data.image.uploaded_at, data.image.modified_at),
        "file": (data.file.pk, data.file.name, data.file.uploaded_at, data.file.modified_at),
        "document": (data.document.pk, data.document.title),
        "page_content": (
            data.page_content.pk,
            data.page_content.title,
            data.page_content.changed_date,
            data.page.pk,
        ),
    }


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.parametrize("run", [1, 2])
def test_scenario_is_identical_across_runs(admin_client, django_user_model, run):
    """Two transactional runs — the DB is flushed and sequences reset between them."""
    data = visual_data_create(admin=django_user_model.objects.get(username="admin"))
    FINGERPRINTS.append(_fingerprint(data))

    if run == 2:
        first, second = FINGERPRINTS
        assert first == second


@pytest.mark.django_db
def test_timestamps_are_pinned(visual_data):
    from .data import FIXED_TIMESTAMP

    assert visual_data.article.created == FIXED_TIMESTAMP
    assert visual_data.image.uploaded_at == FIXED_TIMESTAMP
    assert visual_data.file.modified_at == FIXED_TIMESTAMP
    assert visual_data.folder.created_at == FIXED_TIMESTAMP
    assert visual_data.admin.last_login == FIXED_TIMESTAMP
    assert visual_data.page_content.changed_date == FIXED_TIMESTAMP
