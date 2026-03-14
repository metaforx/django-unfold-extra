import pytest
from playwright.sync_api import expect


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestUserSettingsSubmitRow:
    """Verify that the CMS UserSettings admin uses Unfold's styled submit row."""

    def test_submit_row_has_unfold_styling(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/cms/usersettings/")
        page.wait_for_load_state("networkidle")

        # Unfold's submit row uses id="submit-row" (not class="submit-row")
        submit_row = page.locator("#submit-row")
        expect(submit_row).to_be_visible()

    def test_submit_row_has_styled_save_button(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/cms/usersettings/")
        page.wait_for_load_state("networkidle")

        # Unfold renders <button type="submit" name="_save"> not <input type="submit">
        save_button = page.locator('#submit-row button[name="_save"]')
        expect(save_button).to_be_visible()
        expect(save_button).to_contain_text("Save")

    def test_submit_row_no_plain_django_input(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/cms/usersettings/")
        page.wait_for_load_state("networkidle")

        # Plain Django submit row uses <input type="submit"> — should NOT be present
        plain_input = page.locator('.submit-row input[type="submit"]')
        expect(plain_input).to_have_count(0)
