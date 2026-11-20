"""Regression tests: saving Page advanced settings from the CMS toolbar modal and the sideframe."""

import pytest
from cms.api import create_page
from cms.toolbar.utils import get_object_edit_url
from django.contrib.sites.models import Site
from django.urls import reverse

IFRAME = {"Sec-Fetch-Dest": "iframe"}


def _advanced_settings_data(admin_client, url: str) -> dict:
    form = admin_client.get(url).context["adminform"].form
    return {k: v for k, v in form.initial.items() if v is not None}


@pytest.fixture
def admin_user_obj(admin_client, django_user_model):
    return django_user_model.objects.get(username="admin")


@pytest.fixture
def second_site_page(settings, admin_user_obj):
    """A page on site 2, whose only language (``de``) is not one of site 1's."""
    settings.CMS_LANGUAGES = {
        1: [{"code": "en", "name": "English"}],
        2: [{"code": "de", "name": "Deutsch"}],
    }
    site = Site.objects.create(pk=2, domain="de.example.com", name="de")
    return create_page("Start", "base.html", "de", created_by=admin_user_obj, site=site)


@pytest.mark.django_db
class TestPageAdvancedSettingsModalSave:
    def test_redirects_to_edit_url(self, admin_client, admin_user_obj):
        page = create_page("Home", "base.html", "en", created_by=admin_user_obj)
        url = reverse("admin:cms_page_change", args=[page.pk])
        data = _advanced_settings_data(admin_client, url)
        data["_cms_modal"] = "1"
        response = admin_client.post(url, data, headers=IFRAME)
        assert response.status_code == 200, response.content[:500]
        assert get_object_edit_url(page.get_admin_content("en")) in response.content.decode()

    @pytest.mark.requires_cms("5.1")
    def test_second_site_reopens_editor_in_its_language(self, admin_client, second_site_page):
        url = reverse("admin:cms_page_change", args=[second_site_page.pk]) + "?site=2"
        data = _advanced_settings_data(admin_client, url)
        data["_cms_modal"] = "1"
        response = admin_client.post(url, data, headers=IFRAME)
        assert response.status_code == 200, response.content[:500]
        assert get_object_edit_url(second_site_page.get_admin_content("de")) in response.content.decode()


@pytest.mark.django_db
class TestPageAdvancedSettingsSideframeSave:
    @pytest.mark.requires_cms("5.1")
    def test_second_site_returns_to_its_page_tree(self, admin_client, second_site_page):
        url = reverse("admin:cms_page_change", args=[second_site_page.pk]) + "?site=2"
        data = _advanced_settings_data(admin_client, url)
        response = admin_client.post(url, data, headers=IFRAME)
        assert response.status_code == 200, response.content[:500]
        changelist = reverse("admin:cms_pagecontent_changelist")
        assert f"{changelist}?site=2" in response.content.decode()
