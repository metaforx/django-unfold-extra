"""Every registered view, in light and dark, against its committed reference image.

Deselected by default and only meaningful inside the pinned container: fonts render
differently elsewhere, so a host run would produce references nobody can reproduce.
"""

from __future__ import annotations

import re

import pytest

from .views import VIEWS

THEMES = ("light", "dark")

VIEWPORT_WIDTH = 1440
VIEWPORT_HEIGHT = 900

# One parametrization over the product, so each id is exactly the snapshot file stem.
CASES = [(view, theme) for view in VIEWS for theme in THEMES]
CASE_IDS = [f"{view.name}--{theme}" for view, theme in CASES]

BLUR_SCRIPT = "() => document.activeElement instanceof HTMLElement && document.activeElement.blur()"

SETTLE_SCRIPT = """
() => document.fonts.ready.then(
    () => Array.from(document.images).every(image => image.complete)
)
"""


def _document_height(*, page) -> int:
    """Full document height, never below the standard viewport."""
    height = page.evaluate("() => document.documentElement.scrollHeight")
    return max(int(height), VIEWPORT_HEIGHT)


def _unexpected(*, errors: list[str], allowed: tuple[str, ...]) -> list[str]:
    return [
        error for error in errors if not any(re.search(pattern, error) for pattern in allowed)
    ]


@pytest.mark.visual
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.parametrize("view,theme", CASES, ids=CASE_IDS)
def test_view_matches_reference(themed_page, live_server, visual_data, assert_snapshot, view, theme):
    name = f"{view.name}--{theme}"
    themed = themed_page(theme)
    page = themed.page

    response = page.goto(f"{live_server.url}{view.url(visual_data)}")
    assert response is not None and response.status == view.status, (
        f"{name}: expected {view.status}, got {response.status if response else 'no response'}"
    )

    page.wait_for_load_state("networkidle")
    page.wait_for_function(SETTLE_SCRIPT)
    # Django autofocuses the first form field; whether its ring has painted by capture
    # time is a race, so focus is dropped before every screenshot.
    page.evaluate(BLUR_SCRIPT)

    unexpected = _unexpected(errors=themed.errors, allowed=view.allowed_console_errors)
    assert not unexpected, f"{name}: " + "; ".join(unexpected)

    if view.setup is not None:
        view.setup(page, visual_data)
        page.wait_for_function(SETTLE_SCRIPT)

    if view.full_page:
        # Playwright paints position:fixed chrome once, at its viewport position, then
        # extends the canvas to the whole document — leaving Unfold's submit row floating
        # over the middle of a tall page and hiding what is under it. Growing the viewport
        # to the document first puts that chrome at the real bottom and occludes nothing.
        page.set_viewport_size({"width": VIEWPORT_WIDTH, "height": _document_height(page=page)})
        page.wait_for_function(SETTLE_SCRIPT)

    page.evaluate(BLUR_SCRIPT)

    png = page.screenshot(
        full_page=view.full_page,
        animations="disabled",
        caret="hide",
        mask=[page.locator(selector) for selector in view.mask],
    )
    assert_snapshot(png, name)
