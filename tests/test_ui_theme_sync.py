"""Unfold's and the CMS toolbar's theme switchers must drive each other.

The page tree's colours are keyed on ``html[data-theme]``, which only
``theme-sync.js`` sets. Unfold's switcher changes ``adminTheme`` through Alpine,
the toolbar changes ``data-theme`` and the ``theme`` key, and a ``storage`` event
only fires in *other* windows — so a switch in the same window used to reach
neither the page tree nor the other store (#58).
"""

import pytest
from cms.toolbar.utils import get_object_edit_url
from playwright.sync_api import expect

from tests.visual.data import cms_page_create

PAGETREE = "/admin/cms/pagecontent/"


def switch_theme(page, theme: str) -> None:
    """Do what the Unfold switcher's buttons do: ``x-on:click="adminTheme = '<theme>'"``."""
    page.evaluate(
        "theme => { Alpine.$data(document.documentElement).adminTheme = theme; }",
        theme,
    )


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestPagetreeThemeSwitch:
    @pytest.mark.parametrize("theme", ["dark", "light", "auto"])
    def test_switch_updates_cms_theme(self, authenticated_page, live_server, theme):
        page = authenticated_page
        page.goto(f"{live_server.url}{PAGETREE}")
        page.wait_for_load_state("networkidle")
        start = "light" if theme != "light" else "dark"
        switch_theme(page, start)
        expect(page.locator("html")).to_have_attribute("data-theme", start)

        switch_theme(page, theme)

        expect(page.locator("html")).to_have_attribute("data-theme", theme)
        assert page.evaluate("localStorage.getItem('theme')") == theme

    def test_switch_restyles_pagetree(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}{PAGETREE}")
        page.wait_for_load_state("networkidle")
        background = "getComputedStyle(document.documentElement).getPropertyValue('--dca-white').trim()"
        switch_theme(page, "light")
        expect(page.locator("html")).to_have_attribute("data-theme", "light")
        light = page.evaluate(background)

        switch_theme(page, "dark")
        expect(page.locator("html")).to_have_attribute("data-theme", "dark")

        assert page.evaluate(background) != light


def toolbar_switch(page, theme: str) -> None:
    """Do what the toolbar's colour scheme toggle does, landing on ``theme``."""
    page.evaluate("theme => CMS.API.Helpers.setColorScheme(theme)", theme)


def unfold_theme(page_or_frame) -> str:
    return page_or_frame.evaluate("Alpine.$data(document.documentElement).adminTheme")


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestToolbarThemeSwitch:
    @pytest.fixture
    def frontend(self, fresh_content_type_caches, authenticated_page, live_server, admin_user):
        content = cms_page_create(title="Home", user=admin_user)
        page = authenticated_page
        page.goto(live_server.url + get_object_edit_url(content, language="en"))
        page.wait_for_load_state("networkidle")
        toolbar_switch(page, "light")
        return page

    def open_sideframe(self, page):
        page.evaluate(
            "url => (CMS.API.Sideframe || new CMS.Sideframe()).open({url, animate: false})",
            PAGETREE,
        )
        page.frame_locator(".cms-sideframe-frame iframe").locator("#content").first.wait_for()
        page.wait_for_load_state("networkidle")
        return next(frame for frame in page.frames if PAGETREE in frame.url)

    def test_switch_without_sideframe_reaches_admin(self, frontend, live_server):
        toolbar_switch(frontend, "dark")
        expect(frontend.locator("html")).to_have_attribute("data-theme", "dark")
        assert frontend.evaluate("localStorage.getItem('adminTheme')") == '"dark"'

        admin = frontend.context.new_page()
        admin.goto(f"{live_server.url}{PAGETREE}")
        admin.wait_for_load_state("networkidle")

        expect(admin.locator("html")).to_have_attribute("data-theme", "dark")
        assert unfold_theme(admin) == "dark"

    def test_switch_restyles_sideframe(self, frontend):
        frame = self.open_sideframe(frontend)

        toolbar_switch(frontend, "dark")

        expect(frame.locator("html")).to_have_attribute("data-theme", "dark")
        expect(frame.locator("html")).to_have_class("dark")
        # Unfold's own switcher must show the new theme, or clicking it is a no-op
        assert unfold_theme(frame) == "dark"

    def test_unfold_switch_in_sideframe_reaches_toolbar(self, frontend):
        frame = self.open_sideframe(frontend)

        switch_theme(frame, "dark")

        expect(frontend.locator("html")).to_have_attribute("data-theme", "dark")
        assert frontend.evaluate("localStorage.getItem('theme')") == "dark"
