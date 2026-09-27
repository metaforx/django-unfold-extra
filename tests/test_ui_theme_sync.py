"""Unfold's theme switcher must restyle the CMS page tree in the same window.

The page tree's colours are keyed on ``html[data-theme]``, which only
``theme-sync.js`` sets. Unfold's switcher changes ``adminTheme`` through Alpine,
and a ``storage`` event only fires in *other* windows — so outside the CMS
sideframe nothing used to update the attribute (#58).
"""

import pytest
from playwright.sync_api import expect


def switch_theme(page, theme: str) -> None:
    """Do what the switcher's buttons do: ``x-on:click="adminTheme = '<theme>'"``."""
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
        page.goto(f"{live_server.url}/admin/cms/pagecontent/")
        page.wait_for_load_state("networkidle")
        start = "light" if theme != "light" else "dark"
        switch_theme(page, start)
        expect(page.locator("html")).to_have_attribute("data-theme", start)

        switch_theme(page, theme)

        expect(page.locator("html")).to_have_attribute("data-theme", theme)
        assert page.evaluate("localStorage.getItem('theme')") == theme

    def test_switch_restyles_pagetree(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/cms/pagecontent/")
        page.wait_for_load_state("networkidle")
        background = "getComputedStyle(document.documentElement).getPropertyValue('--dca-white').trim()"
        switch_theme(page, "light")
        expect(page.locator("html")).to_have_attribute("data-theme", "light")
        light = page.evaluate(background)

        switch_theme(page, "dark")
        expect(page.locator("html")).to_have_attribute("data-theme", "dark")

        assert page.evaluate(background) != light
