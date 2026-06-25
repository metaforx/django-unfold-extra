import io
import re

import pytest
from playwright.sync_api import expect


def _make_image(name="ui.png", size=(320, 200)):
    """Build an in-memory uploaded image for filer."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image as PILImage

    buf = io.BytesIO()
    PILImage.new("RGB", size, (120, 160, 200)).save(buf, "PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerSidebarVisible:
    """The filer folder directory-listing view adds a ``filebrowser`` body class.

    Upstream filer ships ``.filebrowser h2{display:none}``, which (since the class
    sits on <body>) also hides Unfold's sidebar navigation group titles — rendered
    as <h2> and doubling as the collapse toggle — making the whole sidebar look
    empty. The Unfold-patched admin_filer.css re-scopes that rule to ``#content``.
    """

    def test_sidebar_titles_visible_on_folder_view(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/")
        page.wait_for_load_state("networkidle")

        # The Unfold sidebar renders app group titles as <h2> inside #nav-sidebar.
        # With the unpatched rule these collapse to display:none.
        first_title = page.locator("#nav-sidebar h2").first
        expect(first_title).to_be_visible()

    def test_sidebar_has_visible_nav_links_on_folder_view(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/")
        page.wait_for_load_state("networkidle")

        # At least one real navigation link must be visible in the sidebar.
        groups_link = page.locator('#nav-sidebar a[href="/admin/auth/group/"]')
        expect(groups_link).to_be_visible()


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerAddFolder:
    """filer's "make folder" popup is served by a custom view whose context lacks
    the standard admin keys. Unfold's change_form.html renders ``{% submit_row %}``
    in the footer (outside the content block), so it fires for this template and
    raises ``KeyError: 'add'``. The contrib.filer override blanks that block and
    renders its own Unfold-styled Save button.
    """

    def test_make_folder_popup_renders_with_save_button(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/make_folder/?_popup=1")
        page.wait_for_load_state("networkidle")

        # Previously this raised a 500 (KeyError: 'add'); the Save button must render.
        save_button = page.locator('#folder_form button[name="_save"], #folder_form input[name="_save"]')
        expect(save_button.first).to_be_visible()


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerImageChangeForm:
    """filer renders the image preview + focal-point (subject location) picker in
    `{% block object-tools %}`, which Unfold's change_form does not output, so the
    image vanished. The contrib.filer override renders filer's native detail_info
    panel into a block Unfold does render, styles the file field with Unfold's
    widget, and adds a folder-path breadcrumb trail.
    """

    def _create_image(self, admin_user):
        from filer.models import Folder, Image

        folder = Folder.objects.create(name="Photos", owner=admin_user)
        return Image.objects.create(
            owner=admin_user,
            folder=folder,
            original_filename="ui.png",
            file=_make_image(),
        )

    def test_image_preview_and_focal_point_visible(self, authenticated_page, live_server, admin_user):
        img = self._create_image(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/image/{img.pk}/change/")
        page.wait_for_load_state("networkidle")

        # The focal-point preview image must render and be visible.
        preview = page.locator("img.js-focal-point-image")
        expect(preview).to_be_visible()
        # Focal-point picker wires to the subject_location field.
        expect(page.locator(".js-focal-point")).to_have_attribute(
            "data-location-selector", "#id_subject_location"
        )

    def test_breadcrumb_trail_in_header_with_folder_targets(self, authenticated_page, live_server, admin_user):
        img = self._create_image(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/image/{img.pk}/change/")
        page.wait_for_load_state("networkidle")

        # The breadcrumb lives in Unfold's header <h1>, using filer folder targets
        # (Filer > Folder > Photos > ...), not the flat model trail.
        header = page.locator("#header-inner h1")
        expect(header.get_by_role("link", name="Filer", exact=True)).to_be_visible()
        expect(header.get_by_role("link", name="Folder", exact=True)).to_be_visible()
        expect(header.get_by_role("link", name="Photos", exact=True)).to_be_visible()

    def test_no_duplicate_breadcrumb_in_content(self, authenticated_page, live_server, admin_user):
        img = self._create_image(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/image/{img.pk}/change/")
        page.wait_for_load_state("networkidle")

        # Only the header breadcrumb should link to the folder; no second trail in
        # the content body.
        content_filer_links = page.locator("#content").get_by_role("link", name="Folder", exact=True)
        expect(content_filer_links).to_have_count(0)

    def test_file_field_uses_unfold_widget(self, authenticated_page, live_server, admin_user):
        img = self._create_image(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/image/{img.pk}/change/")
        page.wait_for_load_state("networkidle")

        # The `file` field lives in filer's collapsed "Advanced" fieldset
        # (rendered as <details>); open every details so it becomes visible.
        page.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")

        # Unfold's styled clearable-file-input wrapper must render around the row.
        wrapper = page.locator(".field-file .grow > div").first
        expect(wrapper).to_be_visible()
        # And it must carry Unfold's Tailwind styling (not a bare input).
        expect(wrapper).to_have_class(re.compile(r"rounded-default"))
