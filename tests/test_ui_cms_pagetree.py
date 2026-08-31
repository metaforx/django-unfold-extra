"""django-cms' page tree stylesheet must not collapse Unfold's nav sidebar.

``cms.pagetree.css`` ships ``.cms-hidden, .hidden {display: none !important}``,
which outranks the Tailwind ``display`` utilities Unfold reveals its sidebar
with. ``pagetree-overrides.css`` re-asserts them; these tests pin the markup it
has to cover, which moves with Unfold releases.
"""

import pytest
from playwright.sync_api import expect

SIDEBAR = {
    "navigation": [
        {
            "title": "Content",
            "items": [
                {"title": "Page contents", "link": "/admin/cms/pagecontent/"},
            ],
        },
    ]
}


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestPagetreeSidebar:
    def test_configured_sidebar_groups_stay_visible(
        self, settings, authenticated_page, live_server
    ):
        """Unfold wraps each configured group in `hidden … has-[ol]:has-[li]:block`."""
        settings.UNFOLD = {**settings.UNFOLD, "SIDEBAR": SIDEBAR}

        page = authenticated_page
        page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{live_server.url}/admin/cms/pagecontent/")
        page.wait_for_load_state("networkidle")

        expect(page.locator("#nav-sidebar-apps")).to_be_visible()
        expect(
            page.locator("#nav-sidebar-apps").get_by_text("Page contents")
        ).to_be_visible()

    def test_app_list_sidebar_stays_visible(self, authenticated_page, live_server):
        """Without a configured navigation, Unfold falls back to the app list."""
        page = authenticated_page
        page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{live_server.url}/admin/cms/pagecontent/")
        page.wait_for_load_state("networkidle")

        expect(page.locator("#nav-sidebar-apps")).to_be_visible()
        expect(page.locator("#nav-sidebar-apps a", has_text="Users")).to_be_visible()
