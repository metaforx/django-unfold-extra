"""Shared fixtures for the visual regression suite."""

from __future__ import annotations

import pytest

from .data import VisualData, visual_data_create


@pytest.fixture(autouse=True)
def visual_media_root(settings, tmp_path_factory) -> None:
    """Keep filer uploads and thumbnails out of the repository.

    ``testapp.settings`` leaves ``MEDIA_ROOT`` unset, so filer would otherwise write
    ``filer_public/`` and ``filer_public_thumbnails/`` into the working directory.
    """
    settings.MEDIA_ROOT = str(tmp_path_factory.mktemp("media"))
    settings.MEDIA_URL = "/media/"


@pytest.fixture
def visual_data(admin_client, django_user_model) -> VisualData:
    """The rendering scenario, owned by the superuser ``admin_client`` logs in.

    Depending on ``admin_client`` keeps that account's creation in one place; requesting
    both fixtures in either order would otherwise race to create the same username.
    """
    return visual_data_create(admin=django_user_model.objects.get(username="admin"))
