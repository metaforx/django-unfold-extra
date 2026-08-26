"""filer's changelist actions render Unfold-styled confirmation pages.

filer ships its own templates for copy/move/rename/resize/delete, built for
Django's stock admin; ``unfold_extra.contrib.filer`` replaces them with the
markup Unfold uses for its own action confirmations. The point of these tests is
that the restyling did not drop any of filer's plumbing — the hidden inputs and
form fields the actions need to actually run.
"""

import io

import pytest

ACTIONS = {
    "copy_files_and_folders": "will be copied",
    "move_files_and_folders": "will be moved",
    "rename_files": "will be renamed",
    "resize_images": "will be resized",
    "delete_files_or_folders": "Are you sure",
}


def _image(name="action.png"):
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image as PILImage

    buf = io.BytesIO()
    PILImage.new("RGB", (32, 20), (120, 160, 200)).save(buf, "PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


@pytest.fixture
def library(django_user_model):
    """A folder holding one image, plus a second folder to copy/move into."""
    from filer.models import Folder, Image

    user = django_user_model.objects.get(username="admin")
    source = Folder.objects.create(name="assets", owner=user)
    target = Folder.objects.create(name="archive", owner=user)
    image = Image.objects.create(
        owner=user, folder=source, original_filename="action.png", file=_image()
    )
    return source, target, image


def _post(admin_client, folder, action, image, **extra):
    return admin_client.post(
        f"/admin/filer/folder/{folder.pk}/list/",
        {"action": action, "_selected_action": [f"file-{image.pk}"], **extra},
    )


@pytest.mark.django_db
class TestConfirmationPages:
    @pytest.mark.parametrize("action,phrase", ACTIONS.items())
    def test_page_is_unfold_styled(self, admin_client, library, action, phrase):
        source, _target, image = library
        response = _post(admin_client, source, action, image)
        html = response.content.decode()

        assert response.status_code == 200
        assert phrase in html
        # Unfold's confirmation card, and its cancel/submit pair.
        assert "border border-base-200 rounded-default shadow-xs" in html
        assert "cancel-link" in html
        assert 'type="submit"' in html

    def test_destination_select_is_unfold_styled(self, admin_client, library):
        source, target, image = library
        html = _post(
            admin_client, source, "copy_files_and_folders", image
        ).content.decode()

        assert f'<option value="{target.pk}"' in html
        # Unfold's own select classes, not a bare browser dropdown.
        assert "appearance-none" in html


@pytest.mark.django_db
class TestActionsStillRun:
    """The confirmed action goes through — i.e. the rewritten templates still
    carry filer's hidden inputs and form fields."""

    def test_copy(self, admin_client, library):
        from filer.models import File

        source, target, image = library
        _post(
            admin_client,
            source,
            "copy_files_and_folders",
            image,
            post="yes",
            destination=target.pk,
            suffix="",
        )

        assert File.objects.filter(folder=target).count() == 1

    def test_move(self, admin_client, library):
        source, target, image = library
        _post(
            admin_client,
            source,
            "move_files_and_folders",
            image,
            post="yes",
            destination=target.pk,
        )
        image.refresh_from_db()

        assert image.folder == target

    def test_rename(self, admin_client, library):
        source, _target, image = library
        _post(
            admin_client,
            source,
            "rename_files",
            image,
            post="yes",
            rename_format="renamed-%(original_filename)s",
        )
        image.refresh_from_db()

        assert image.name == "renamed-action.png"

    def test_delete(self, admin_client, library):
        from filer.models import File

        source, _target, image = library
        _post(admin_client, source, "delete_files_or_folders", image, post="yes")

        assert not File.objects.filter(pk=image.pk).exists()


@pytest.mark.django_db
class TestNewFolderPage:
    """filer's "New Folder" popup is styled and still creates the folder.

    The page runs its own view (``filer.admin.views.make_folder``) rather than a
    changelist action, so it carries the confirmation-card shell itself — and its
    form is built outside a ``ModelAdmin``, which is why the widget is patched.
    """

    URL = "/admin/filer/folder/make_folder/"

    def test_page_is_unfold_styled(self, admin_client):
        html = admin_client.get(self.URL).content.decode()

        assert "border border-base-200 rounded-default shadow-xs" in html
        assert "cancel-link" in html
        # The name input carries Unfold's widget classes, not the stock admin's.
        assert 'class="vTextField"' not in html
        assert 'maxlength="255"' in html
        assert "rounded-default shadow-xs text-font-default-light" in html

    def test_creates_folder(self, admin_client):
        from filer.models import Folder

        response = admin_client.post(self.URL, {"name": "new-folder"})

        assert response.status_code == 200
        assert Folder.objects.filter(name="new-folder").exists()

    def test_duplicate_name_shows_unfold_error(self, admin_client, django_user_model):
        from filer.models import Folder

        user = django_user_model.objects.get(username="admin")
        Folder.objects.create(name="assets", owner=user)

        html = admin_client.post(self.URL, {"name": "assets"}).content.decode()

        assert "Folder with this name already exists." in html
        assert "errornote" in html
