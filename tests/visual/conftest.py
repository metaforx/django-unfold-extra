"""Shared fixtures for the visual regression suite."""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from PIL import Image

from tests.conftest import UPDATED_SNAPSHOTS, admin_login

from .data import VisualData, visual_data_create
from .snapshot import snapshot_compare, snapshot_write_results


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


@pytest.fixture
def snapshots_dir() -> Path:
    """Committed reference images. Tests override this with ``tmp_path``."""
    return Path(__file__).parent / "snapshots"


@pytest.fixture
def results_dir() -> Path:
    """Untracked expected/actual/diff output for failures."""
    return Path(__file__).parent / "results"


@pytest.fixture
def assert_snapshot(pytestconfig, snapshots_dir, results_dir):
    """Compare a PNG against its committed reference.

    Missing reference: written, then fail — a new view never passes silently.
    ``--update-snapshots``: overwrite and pass, recording the name for the summary.
    Mismatch: write the triplet and fail with the differing ratio.
    """

    def _assert_snapshot(png: bytes, name: str) -> None:
        actual = Image.open(io.BytesIO(png))
        reference = snapshots_dir / f"{name}.png"
        update = pytestconfig.getoption("--update-snapshots")

        if not reference.exists():
            snapshots_dir.mkdir(parents=True, exist_ok=True)
            actual.save(reference)
            if update:
                pytestconfig.stash[UPDATED_SNAPSHOTS].append(name)
                return
            pytest.fail(f"{name}: no reference image; wrote {reference} — review it and commit")

        result = snapshot_compare(expected=Image.open(reference), actual=actual)
        if result.passed:
            return

        if update:
            actual.save(reference)
            pytestconfig.stash[UPDATED_SNAPSHOTS].append(name)
            return

        written = snapshot_write_results(name=name, result=result, results_dir=results_dir)
        pytest.fail(f"{name}: {result.summary}; wrote {', '.join(path.name for path in written)}")

    return _assert_snapshot


@dataclass(frozen=True)
class ThemedPage:
    """A logged-in page plus everything that went wrong while it loaded."""

    page: object
    errors: list[str]


@pytest.fixture
def themed_page(browser, live_server):
    """Factory for a logged-in page pinned to one theme and a fixed rendering environment.

    The theme is written before any page script runs, so Unfold's skeleton reads it on
    first paint and the screenshot never catches a flash of the other theme.
    """
    contexts = []

    def _themed_page(theme: str) -> ThemedPage:
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
            color_scheme=theme,
            reduced_motion="reduce",
            locale="en-US",
            timezone_id="UTC",
        )
        contexts.append(context)
        # ``adminTheme`` is JSON-encoded; ``sidebarDesktopOpen`` is Unfold's '1'/'0' flag.
        context.add_init_script(
            f"localStorage.setItem('adminTheme', {json.dumps(json.dumps(theme))});"
            "localStorage.setItem('sidebarDesktopOpen', '1');"
        )

        errors: list[str] = []
        page = admin_login(
            context=context,
            live_server=live_server,
            username="admin",
            password="password",
        )
        page.on(
            "console",
            lambda message: errors.append(f"console error: {message.text}")
            if message.type == "error"
            else None,
        )
        page.on("pageerror", lambda error: errors.append(f"page error: {error}"))
        page.on(
            "response",
            lambda response: errors.append(f"HTTP {response.status}: {response.url}")
            if response.status >= 400 and response.url.startswith(live_server.url)
            else None,
        )
        return ThemedPage(page=page, errors=errors)

    yield _themed_page

    for context in contexts:
        context.close()
