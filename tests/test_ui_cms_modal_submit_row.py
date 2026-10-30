"""Unfold's submit row must stay hidden inside CMS modals, with or without ``_popup=1``.

django CMS 5.0.10+ opens toolbar modals with ``_popup=1``. Unfold then renders its
submit row without the ``#submit-row`` id, which the modal CSS used to rely on, so a
second submit row showed up next to the CMS modal footer. The row is hidden regardless
of which buttons it contains (e.g. only "Close" when the user cannot save).
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from playwright.sync_api import expect

UNFOLD_SUBMIT_ROW = "#page #main div.relative.z-40:has(.lg\\:scrollable-top)"


def _enter_cms_modal(page):
    # The CMS modal JS adds these classes to the iframe body once it has loaded.
    page.evaluate("document.body.classList.add('cms-admin', 'cms-admin-modal')")


def _assert_row_hidden_in_modal(page, url):
    page.goto(url)
    page.wait_for_load_state("networkidle")
    row = page.locator(UNFOLD_SUBMIT_ROW)
    # Guard: to_be_hidden() also passes for missing elements, so pin the markup first.
    expect(row).to_have_count(1)
    expect(row).to_be_visible()

    _enter_cms_modal(page)
    expect(row).to_be_hidden()


@pytest.fixture
def view_only_page(browser, live_server, db):
    """Staff user who may only view groups, so Unfold renders a row with just "Close"."""
    user = get_user_model().objects.create_user(
        username="viewer", password="testpass", is_staff=True
    )
    user.user_permissions.add(Permission.objects.get(codename="view_group"))
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{live_server.url}/admin/login/?next=/admin/")
    page.fill("#id_username", "viewer")
    page.fill("#id_password", "testpass")
    page.click("[type=submit]")
    page.wait_for_load_state("networkidle")
    yield page
    context.close()


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestCmsModalSubmitRow:
    @pytest.mark.parametrize("query", ["", "?_popup=1"])
    def test_unfold_submit_row_hidden_in_cms_modal(
        self, authenticated_page, live_server, query
    ):
        _assert_row_hidden_in_modal(
            authenticated_page, f"{live_server.url}/admin/cms/usersettings/add/{query}"
        )

    @pytest.mark.parametrize("query", ["", "?_popup=1"])
    def test_submit_row_without_save_button_hidden_in_cms_modal(
        self, view_only_page, live_server, query
    ):
        group = Group.objects.create(name="Editors")
        page = view_only_page
        url = f"{live_server.url}/admin/auth/group/{group.pk}/change/{query}"
        page.goto(url)
        page.wait_for_load_state("networkidle")
        expect(page.locator(f"{UNFOLD_SUBMIT_ROW} button[name='_save']")).to_have_count(0)

        _assert_row_hidden_in_modal(page, url)

    def test_unfold_submit_row_visible_outside_cms_modal(
        self, authenticated_page, live_server
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/cms/usersettings/add/")
        page.wait_for_load_state("networkidle")

        expect(page.locator(UNFOLD_SUBMIT_ROW)).to_be_visible()
