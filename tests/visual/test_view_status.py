"""Every registered view answers with its expected status.

This is the browserless half of the visual suite: it runs in the default test run, so
CI catches a view that starts 404ing or raising after a dependency bump.
"""

from __future__ import annotations

import pytest
from django.test import Client

from .views import VIEWS


@pytest.mark.django_db
@pytest.mark.parametrize("view", VIEWS, ids=[view.name for view in VIEWS])
def test_view_returns_expected_status(admin_client, visual_data, view):
    url = view.url(visual_data)
    # Not the ``client`` fixture: ``admin_client`` logs that same instance in.
    response = (admin_client if view.auth else Client()).get(url)

    assert response.status_code == view.status, (
        f"{view.name}: GET {url} returned {response.status_code}, expected {view.status}"
    )
