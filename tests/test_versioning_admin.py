"""Regression tests: every djangocms-versioning admin view renders with Unfold templates.

djangocms-versioning moves templates between releases (2.6 moved ``grouper_form.html``),
which silently drops our overrides and breaks Unfold's ``submit_row`` (``KeyError: 'add'``).
"""

import pytest
from cms.api import create_page
from django.urls import reverse
from djangocms_versioning.constants import ARCHIVED, DRAFT, PUBLISHED
from djangocms_versioning.models import Version


def _version_url(name, *args):
    return reverse(f"admin:djangocms_versioning_pagecontentversion_{name}", args=args)


def _state(version):
    # django-fsm protects ``state``: ``refresh_from_db()`` raises, so re-query.
    return Version.objects.get(pk=version.pk).state


def _template_origins(response):
    return [template.origin.name for template in response.templates if template.origin]


@pytest.fixture
def admin_user_obj(admin_client, django_user_model):
    return django_user_model.objects.get(username="admin")


@pytest.fixture
def versions(admin_user_obj):
    """A page with an archived, a published and a draft version (``en``)."""
    page = create_page("Home", "base.html", "en", created_by=admin_user_obj)
    archived = Version.objects.get(object_id=page.get_admin_content("en").pk)
    archived.archive(admin_user_obj)
    published = archived.copy(admin_user_obj)
    published.publish(admin_user_obj)
    draft = published.copy(admin_user_obj)
    return {"page": page, ARCHIVED: archived, PUBLISHED: published, DRAFT: draft}


@pytest.mark.django_db
class TestVersioningAdminViews:
    def test_fixture_states(self, versions):
        for state in (ARCHIVED, PUBLISHED, DRAFT):
            assert _state(versions[state]) == state

    def test_grouper_select(self, admin_client, versions):
        response = admin_client.get(_version_url("grouper"))
        assert response.status_code == 200
        assert any(
            "unfold_extra" in origin and origin.endswith("grouper_form.html")
            for origin in _template_origins(response)
        ), "unfold_extra grouper_form.html override not used"

    def test_changelist_without_grouper_redirects_to_select(self, admin_client, versions):
        response = admin_client.get(_version_url("changelist"))
        assert response.status_code == 302
        assert response.url == _version_url("grouper")

    @pytest.mark.parametrize("language", ["en", "de"])
    def test_changelist(self, admin_client, versions, language):
        response = admin_client.get(
            _version_url("changelist"), {"page": versions["page"].pk, "language": language}
        )
        assert response.status_code == 200

    def test_compare(self, admin_client, versions):
        response = admin_client.get(_version_url("compare", versions[PUBLISHED].pk))
        assert response.status_code == 200

    def test_compare_to(self, admin_client, versions):
        response = admin_client.get(
            _version_url("compare", versions[PUBLISHED].pk),
            {"compare_to": versions[DRAFT].pk, "back": "/admin/"},
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        ("view_name", "state"),
        [
            ("archive", DRAFT),
            ("discard", DRAFT),
            ("unpublish", PUBLISHED),
            ("revert", ARCHIVED),
        ],
    )
    def test_confirmation(self, admin_client, versions, view_name, state):
        response = admin_client.get(_version_url(view_name, versions[state].pk))
        assert response.status_code == 200

    def test_publish(self, admin_client, versions):
        response = admin_client.post(_version_url("publish", versions[DRAFT].pk))
        assert response.status_code == 302
        assert _state(versions[DRAFT]) == PUBLISHED

    def test_publish_rejects_get(self, admin_client, versions):
        response = admin_client.get(_version_url("publish", versions[DRAFT].pk))
        assert response.status_code == 405

    def test_edit_redirect(self, admin_client, versions):
        response = admin_client.post(_version_url("edit_redirect", versions[DRAFT].pk))
        assert response.status_code == 302


@pytest.mark.django_db
class TestVersionedPageContentAdmin:
    def test_pagetree(self, admin_client, versions):
        response = admin_client.get(reverse("admin:cms_pagecontent_changelist"))
        assert response.status_code == 200

    @pytest.mark.parametrize("state", [DRAFT, PUBLISHED])
    def test_change_form(self, admin_client, versions, state):
        content = versions[state].content
        response = admin_client.get(reverse("admin:cms_pagecontent_change", args=[content.pk]))
        assert response.status_code == 200
        assert any(
            "unfold_extra" in origin and origin.endswith("djangocms_versioning/page/change_form.html")
            for origin in _template_origins(response)
        ), "unfold_extra versioning page change_form.html override not used"

    def test_change_form_versioning_js_is_served(self, admin_client, versions):
        from django.contrib.staticfiles import finders

        from unfold_extra.templatetags.unfold_extra_tags import _versioning_admin_js_path

        assert finders.find(_versioning_admin_js_path())
        content = versions[DRAFT].content
        response = admin_client.get(reverse("admin:cms_pagecontent_change", args=[content.pk]))
        assert _versioning_admin_js_path() in response.content.decode()
