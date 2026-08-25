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


def _folder_with_files(admin_user, name="assets"):
    """One folder holding a subfolder and two images."""
    from filer.models import Folder, Image

    folder = Folder.objects.create(name=name, owner=admin_user)
    Folder.objects.create(name="nested", parent=folder, owner=admin_user)
    for filename in ("a.png", "b.png"):
        Image.objects.create(
            owner=admin_user,
            folder=folder,
            original_filename=filename,
            file=_make_image(filename),
        )
    return folder


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerSidebarVisible:
    """Unfold's sidebar stays visible on filer's directory listing."""

    def test_sidebar_titles_visible_on_folder_view(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/")
        page.wait_for_load_state("networkidle")

        expect(page.locator("#nav-sidebar h2").first).to_be_visible()

    def test_sidebar_has_visible_nav_links_on_folder_view(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/")
        page.wait_for_load_state("networkidle")

        expect(page.locator('#nav-sidebar a[href="/admin/auth/group/"]')).to_be_visible()


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerDirectoryListingHeader:
    """The directory listing renders Unfold's header with filer's folder trail."""

    def test_root_listing_shows_filer_breadcrumb(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/")
        page.wait_for_load_state("networkidle")

        header = page.locator("#header-inner h1")
        expect(header.get_by_role("link", name="Filer", exact=True)).to_be_visible()
        expect(header.get_by_role("link", name="Folder", exact=True)).to_be_visible()

    def test_nested_listing_shows_ancestor_trail(self, authenticated_page, live_server, admin_user):
        from filer.models import Folder

        parent = Folder.objects.create(name="Photos", owner=admin_user)
        child = Folder.objects.create(name="2024", parent=parent, owner=admin_user)

        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/{child.pk}/list/")
        page.wait_for_load_state("networkidle")

        header = page.locator("#header-inner h1")
        # Ancestors link; the current folder is the trailing plain-text crumb.
        expect(header.get_by_role("link", name="Photos", exact=True)).to_be_visible()
        expect(header).to_contain_text("2024")

    def test_crumbs_keep_verbatim_casing(self, authenticated_page, live_server, admin_user):
        """Crumbs are file names, so they are not capitalised."""
        from filer.models import Folder

        parent = Folder.objects.create(name="photos", owner=admin_user)
        child = Folder.objects.create(name="raw", parent=parent, owner=admin_user)

        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/{child.pk}/list/")
        page.wait_for_load_state("networkidle")

        header = page.locator("#header-inner h1")
        expect(header.get_by_role("link", name="photos", exact=True)).to_be_visible()
        expect(header).to_contain_text("raw")
        assert "Photos" not in header.inner_text()

    def test_placeholder_heading_does_not_leak_into_header(self, authenticated_page, live_server):
        """filer's content_title spacer is not nested inside Unfold's <h1>."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/")
        page.wait_for_load_state("networkidle")

        expect(page.locator("#header-inner h1 h2")).to_have_count(0)


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerListingSelection:
    """Selecting items updates the counter, the rows and filer's toolbar."""

    def test_table_view_selection_updates_counter_and_toolbar(
        self, authenticated_page, live_server, admin_user
    ):
        folder = _folder_with_files(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/{folder.pk}/list/?_list_type=tb")
        page.wait_for_load_state("networkidle")

        page.locator("input.action-select").first.check()

        # filer renders two counters; both must track the selection.
        for counter in page.locator("span.action-counter").all():
            expect(counter).to_have_text(re.compile(r"^1 of 3 selected"))
        # filer's toolbar buttons key off these two classes.
        expect(page.locator(".navigator-table tbody tr.selected")).to_have_count(1)
        expect(page.locator(".actions-wrapper")).to_have_class(re.compile(r"action-selected"))

    def test_table_view_select_all_cascades(self, authenticated_page, live_server, admin_user):
        folder = _folder_with_files(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/{folder.pk}/list/?_list_type=tb")
        page.wait_for_load_state("networkidle")

        page.locator("#action-toggle").check()

        expect(page.locator("span.action-counter").first).to_have_text(
            re.compile(r"^3 of 3 selected")
        )
        expect(page.locator(".navigator-table tbody tr.selected")).to_have_count(3)

    def test_thumbnail_view_files_toggle_selects_only_files(
        self, authenticated_page, live_server, admin_user
    ):
        folder = _folder_with_files(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/{folder.pk}/list/?_list_type=th")
        page.wait_for_load_state("networkidle")

        page.locator("#files-action-toggle").check()

        expect(page.locator('input.action-select[value^="file-"]:checked')).to_have_count(2)
        expect(page.locator('input.action-select[value^="folder-"]:checked')).to_have_count(0)
        expect(page.locator("span.action-counter").first).to_have_text(
            re.compile(r"^2 of 3 selected")
        )


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerAddFolder:
    """The "make folder" popup renders instead of raising KeyError: 'add'."""

    def test_make_folder_popup_renders_with_save_button(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/folder/make_folder/?_popup=1")
        page.wait_for_load_state("networkidle")

        save_button = page.locator('#folder_form button[name="_save"], #folder_form input[name="_save"]')
        expect(save_button.first).to_be_visible()


@pytest.mark.ui
@pytest.mark.django_db(transaction=True)
class TestFilerImageChangeForm:
    """The file/image change form keeps filer's preview, widget and folder trail."""

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

        expect(page.locator("img.js-focal-point-image")).to_be_visible()
        expect(page.locator(".js-focal-point")).to_have_attribute(
            "data-location-selector", "#id_subject_location"
        )

    def test_breadcrumb_trail_in_header_with_folder_targets(self, authenticated_page, live_server, admin_user):
        img = self._create_image(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/image/{img.pk}/change/")
        page.wait_for_load_state("networkidle")

        header = page.locator("#header-inner h1")
        expect(header.get_by_role("link", name="Filer", exact=True)).to_be_visible()
        expect(header.get_by_role("link", name="Folder", exact=True)).to_be_visible()
        expect(header.get_by_role("link", name="Photos", exact=True)).to_be_visible()

    def test_no_duplicate_breadcrumb_in_content(self, authenticated_page, live_server, admin_user):
        """Only the header carries a trail; the content body has none."""
        img = self._create_image(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/image/{img.pk}/change/")
        page.wait_for_load_state("networkidle")

        content_filer_links = page.locator("#content").get_by_role("link", name="Folder", exact=True)
        expect(content_filer_links).to_have_count(0)

    def test_folder_trail_does_not_leak_to_other_filer_models(
        self, authenticated_page, live_server, admin_user
    ):
        """Non-file filer models keep Unfold's default app/model/object trail."""
        from filer.models import ThumbnailOption

        option = ThumbnailOption.objects.create(name="big", width=1600, height=1000)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/thumbnailoption/{option.pk}/change/")
        page.wait_for_load_state("networkidle")

        header = page.locator("#header-inner h1")
        expect(header.get_by_role("link", name="Thumbnail options", exact=True)).to_be_visible()
        expect(header.get_by_role("link", name="Folder", exact=True)).to_have_count(0)

    def test_file_field_uses_unfold_widget(self, authenticated_page, live_server, admin_user):
        img = self._create_image(admin_user)
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/filer/image/{img.pk}/change/")
        page.wait_for_load_state("networkidle")

        # The `file` field sits in filer's collapsed "Advanced" fieldset.
        page.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")

        wrapper = page.locator(".field-file .grow > div").first
        expect(wrapper).to_be_visible()
        expect(wrapper).to_have_class(re.compile(r"rounded-default"))
