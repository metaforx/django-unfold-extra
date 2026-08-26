import io

import pytest
from playwright.sync_api import expect


def _make_image(name="widget.png"):
    """Build an in-memory uploaded image for filer."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image as PILImage

    buf = io.BytesIO()
    PILImage.new("RGB", (320, 200), (120, 160, 200)).save(buf, "PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


# A 1x1 PNG, dropped onto the widget the way a browser delivers a real drag.
DROP_FILE = """
(el) => {
    const png = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
    const bytes = Uint8Array.from(atob(png), c => c.charCodeAt(0));
    const transfer = new DataTransfer();
    transfer.items.add(new File([bytes], 'dropped.png', {type: 'image/png'}));
    el.dispatchEvent(new DragEvent('drop', {bubbles: true, cancelable: true, dataTransfer: transfer}));
}
"""


def _document(admin_user):
    """A testapp.Document with a filer file attached."""
    from filer.models import Folder, Image
    from testapp.models import Document

    folder = Folder.objects.create(name="assets", owner=admin_user)
    image = Image.objects.create(
        owner=admin_user,
        folder=folder,
        original_filename="widget.png",
        file=_make_image(),
    )
    return Document.objects.create(title="doc", file=image, cover=image)


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerWidgetOnUnfoldChangeForm:
    """filer's file widget stays inside its box, with filer's own controls.

    filer scopes its widget layout under ``form .form-row``, which Unfold puts on
    every fieldset row as well — so filer's rules apply and misfire (see the
    django-filer widget block in unfold_extra/src/css/unfold_extra.css).
    """

    def test_controls_stay_inside_the_widget(self, authenticated_page, live_server, admin_user):
        doc = _document(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/document/{doc.pk}/change/")

        widget = page.locator(".filer-widget").first
        box = widget.locator(".filer-dropzone").bounding_box()

        for control in ("a.filerClearer", "a.js-related-edit", "a.js-related-lookup"):
            rect = widget.locator(control).bounding_box()
            assert rect is not None, f"{control} is not rendered"
            assert rect["y"] >= box["y"] - 1, f"{control} escapes the widget above"
            assert rect["y"] + rect["height"] <= box["y"] + box["height"] + 1, (
                f"{control} escapes the widget below, covering the next field"
            )

    def test_file_name_is_visible(self, authenticated_page, live_server, admin_user):
        doc = _document(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/document/{doc.pk}/change/")

        expect(page.locator(".filer-widget .description_text").first).to_have_text("widget.png")
        # filer marks the drop hint hidden once a file is attached.
        expect(page.locator(".filer-widget .dz-message").first).to_be_hidden()

    def test_unfold_related_widget_menu_is_hidden(self, authenticated_page, live_server, admin_user):
        """Unfold's ⋮ menu never worked here: its links only get an ``href`` from
        RelatedObjectLookups.js when the widget is a ``<select>``, and filer's is
        a hidden input. filer hides Django's related links itself, for markup
        Unfold no longer renders."""
        doc = _document(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/document/{doc.pk}/change/")

        menu = page.locator(".related-widget-wrapper:has(.filer-widget) [x-ref^=relatedWidgetWrapper]")
        expect(menu.first).to_be_hidden()

    def test_lookup_button_opens_filer_popup(self, authenticated_page, live_server, admin_user):
        doc = _document(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/document/{doc.pk}/change/")

        with page.expect_popup() as popup_info:
            page.locator(".filer-widget a.js-related-lookup").first.click()

        popup = popup_info.value
        popup.wait_for_load_state()
        assert "_pick=file" in popup.url
        popup.close()

    def test_dropped_file_looks_like_a_saved_one(
        self, authenticated_page, live_server, admin_user
    ):
        """A drop leaves two `.filerFile` elements in the widget: dropzone.js' clone
        of filer's template (thumbnail, name, remove button) and the original
        selector, which filer keeps for its buttons and forces to `display: block`.
        They have to read as the one row the saved state shows."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/document/add/")

        widget = page.locator(".filer-widget").first
        widget.locator(".filer-dropzone").evaluate(DROP_FILE)
        preview = widget.locator(".filer-dropzone > .filerFile:not(.js-file-selector)")
        expect(preview).to_be_visible()
        expect(preview.locator(".dz-name")).to_have_text("dropped.png")

        box = widget.locator(".filer-dropzone").bounding_box()
        controls = widget.locator(
            ".filerFile .filerClearer:visible, .filerFile .related-lookup:visible"
        )
        rows = set()
        for i in range(controls.count()):
            rect = controls.nth(i).bounding_box()
            assert rect["y"] >= box["y"] - 1
            assert rect["y"] + rect["height"] <= box["y"] + box["height"] + 1
            rows.add(round(rect["y"]))

        assert len(rows) == 1, f"controls are stacked, not in one row: {rows}"
        # One clear button, not the clone's *and* the selector's.
        assert controls.count() == 3, f"expected clear/edit/lookup, got {controls.count()}"
