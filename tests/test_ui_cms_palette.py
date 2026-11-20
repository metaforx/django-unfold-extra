"""django CMS's pre-5.1 palette is selected everywhere CMS UI appears, before first paint.

Our CMS overrides are styled against that palette. django CMS 5.1 only applies it under
``html[data-cms-theme="4"]``, which ``theme-sync.js`` sets; on 5.0 the attribute is inert.
"""

import pytest
from cms.toolbar.utils import get_object_edit_url
from playwright.sync_api import expect

from tests.visual.data import cms_page_create
from tests.visual.views import _page_settings_modal_open

PALETTE = ("data-cms-theme", "4")

# Records the attribute at the moment <body> is inserted, i.e. before any content can paint.
RECORD_AT_BODY = """
new MutationObserver(function (_, observer) {
    if (!document.body) return;
    window.__cmsThemeAtBody = document.documentElement.getAttribute('data-cms-theme');
    observer.disconnect();
}).observe(document, {childList: true, subtree: true});
"""

# theme-sync.js must be a blocking <script src> in <head>; defer/async would run it after paint.
THEME_SYNC_TAGS = """
() => Array.from(document.querySelectorAll('script[src*="unfold_extra/js/theme-sync"]')).map(
    s => ({inHead: document.head.contains(s), defer: s.defer, async: s.async, module: s.type === 'module'})
)
"""


@pytest.fixture
def frontend_url(fresh_content_type_caches, admin_user, live_server):
    content = cms_page_create(title="Home", user=admin_user)
    return live_server.url + get_object_edit_url(content, language="en")


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestCmsPalette:
    def test_admin_page(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/")
        expect(page.locator("html")).to_have_attribute(*PALETTE)

    def test_frontend_edit_mode(self, authenticated_page, frontend_url):
        page = authenticated_page
        page.goto(frontend_url)
        expect(page.locator("html")).to_have_attribute(*PALETTE)

    def test_page_settings_modal(self, authenticated_page, frontend_url):
        page = authenticated_page
        page.goto(frontend_url)
        page.wait_for_load_state("networkidle")
        _page_settings_modal_open(page, None)
        expect(page.frame_locator(".cms-modal iframe").locator("html")).to_have_attribute(*PALETTE)


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestCmsPaletteBeforePaint:
    @pytest.fixture
    def recording_page(self, authenticated_page):
        authenticated_page.context.add_init_script(RECORD_AT_BODY)
        return authenticated_page

    def _assert_set_before_body(self, page, url):
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        assert page.evaluate("window.__cmsThemeAtBody") == PALETTE[1]
        tags = page.evaluate(THEME_SYNC_TAGS)
        assert tags == [{"inHead": True, "defer": False, "async": False, "module": False}]

    def test_admin_page(self, recording_page, live_server):
        self._assert_set_before_body(recording_page, f"{live_server.url}/admin/")

    def test_frontend_edit_mode(self, recording_page, frontend_url):
        self._assert_set_before_body(recording_page, frontend_url)
