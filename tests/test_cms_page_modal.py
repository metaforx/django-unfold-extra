"""Regression tests: saving Page advanced settings from the CMS toolbar modal."""

import pytest
from cms.api import create_page
from cms.toolbar.utils import get_object_edit_url
from django.test import RequestFactory
from django.urls import reverse

from unfold_extra.contrib.cms.utils import _language_from_request


@pytest.mark.django_db
class TestLanguageFromRequest:
    def test_without_language_param(self):
        assert _language_from_request(RequestFactory().get("/")) == "en"

    def test_language_param_wins(self):
        assert _language_from_request(RequestFactory().get("/", {"language": "de"})) == "de"


@pytest.mark.django_db
class TestPageAdvancedSettingsModalSave:
    def test_modal_save_redirects_to_edit_url(self, admin_client, django_user_model):
        user = django_user_model.objects.get(username="admin")
        page = create_page("Home", "base.html", "en", created_by=user)
        url = reverse("admin:cms_page_change", args=[page.pk])
        form = admin_client.get(url).context["adminform"].form
        data = {k: v for k, v in form.initial.items() if v is not None}
        data["_cms_modal"] = "1"
        response = admin_client.post(url, data, headers={"Sec-Fetch-Dest": "iframe"})
        assert response.status_code == 200, response.content[:500]
        assert get_object_edit_url(page.get_admin_content("en")) in response.content.decode()
