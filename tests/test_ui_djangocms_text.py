"""djangocms-text editors under Unfold (#52).

djangocms-text gives the editor of an ``HTMLField`` a fixed height with
``overflow-y: auto`` and ``resize: vertical``. A ``!overflow-y-visible`` in our
CSS once overrode that, so long text spilled out of the box and got clipped.
The text plugin's modal hides its only label, yet Unfold's row kept that label's
column from ``lg`` up, pushing the editor right in a wide modal.
"""

import pytest
from cms.api import add_plugin
from cms.toolbar.utils import get_object_edit_url
from django.urls import reverse
from playwright.sync_api import expect
from testapp.models import Note

from tests.visual.data import cms_page_create

BODY = "".join(f"<p>Paragraph {i}: lorem ipsum dolor sit amet.</p>" for i in range(60))
EDITOR = ".cms-editor-inline-wrapper .tiptap"


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestHTMLFieldEditor:
    def test_long_text_scrolls_inside_editor(self, authenticated_page, live_server):
        note = Note.objects.create(title="Long note", body=BODY)
        page = authenticated_page
        page.goto(live_server.url + reverse("admin:testapp_note_change", args=[note.pk]))
        editor = page.locator(EDITOR)
        expect(editor).to_be_visible()

        style = editor.evaluate(
            "e => ({overflowY: getComputedStyle(e).overflowY, height: e.clientHeight, content: e.scrollHeight})"
        )

        assert style["overflowY"] == "auto"
        assert style["content"] > style["height"]


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestTextPluginEditor:
    def test_editor_spans_wide_modal(self, fresh_content_type_caches, authenticated_page, live_server, admin_user):
        content = cms_page_create(title="Home", user=admin_user)
        placeholder = content.get_placeholders().get(slot="content")
        text = add_plugin(placeholder, "TextPlugin", "en", body="<p>Text</p>")
        page = authenticated_page
        page.set_viewport_size({"width": 1800, "height": 900})
        page.goto(live_server.url + get_object_edit_url(content, language="en"))
        page.wait_for_load_state("networkidle")
        page.evaluate(
            "url => new CMS.Modal().open({url, title: 'Text'})",
            f"/admin/cms/placeholder/edit-plugin/{text.pk}/",
        )
        editor = page.frame_locator(".cms-modal iframe").locator(EDITOR)
        expect(editor).to_be_visible()

        # the iframe is wider than Unfold's lg breakpoint, where the label column appears
        left = editor.evaluate("e => e.getBoundingClientRect().left")

        assert left < 60
