"""Smoke tests to verify admin registration and page access work with Unfold styling."""

import pytest
from django.contrib.admin.sites import site as admin_site
from django.urls import reverse


@pytest.mark.django_db
class TestAdminRegistered:
    """Verify all models are registered with the admin site."""

    def test_testapp_models_registered(self):
        registered_models = [model.__name__ for model in admin_site._registry.keys()]
        for model_name in ["Category", "Article", "SimpleModel"]:
            assert model_name in registered_models, f"{model_name} not registered"

    def test_cms_page_registered(self):
        """Verify CMS Page model is registered (re-registered by unfold_extra.contrib.cms)."""
        registered_models = [model.__name__ for model in admin_site._registry.keys()]
        assert "Page" in registered_models
        assert "PageContent" in registered_models

    def test_auth_models_registered(self):
        """Verify auth models are registered (re-registered by unfold_extra.contrib.auth)."""
        registered_models = [model.__name__ for model in admin_site._registry.keys()]
        assert "User" in registered_models
        assert "Group" in registered_models

    def test_site_model_registered(self):
        """Verify Site model is registered (re-registered by unfold_extra.contrib.sites)."""
        registered_models = [model.__name__ for model in admin_site._registry.keys()]
        assert "Site" in registered_models


@pytest.mark.django_db
class TestAdminAccess:
    """Verify admin pages are accessible with Unfold styling."""

    def test_admin_index(self, admin_client):
        response = admin_client.get("/admin/")
        assert response.status_code == 200

    def test_simple_model_changelist(self, admin_client):
        response = admin_client.get("/admin/testapp/simplemodel/")
        assert response.status_code == 200

    def test_simple_model_add(self, admin_client):
        response = admin_client.get("/admin/testapp/simplemodel/add/")
        assert response.status_code == 200

    def test_category_changelist(self, admin_client):
        response = admin_client.get("/admin/testapp/category/")
        assert response.status_code == 200

    def test_category_add(self, admin_client):
        response = admin_client.get("/admin/testapp/category/add/")
        assert response.status_code == 200

    def test_article_changelist(self, admin_client):
        response = admin_client.get("/admin/testapp/article/")
        assert response.status_code == 200

    def test_article_add(self, admin_client):
        response = admin_client.get("/admin/testapp/article/add/")
        assert response.status_code == 200

    def test_cms_usersettings_back_link_targets_cms_app_list(self, admin_client):
        response = admin_client.get("/de/admin/cms/usersettings/")
        assert response.status_code == 200
        assert reverse("admin:app_list", kwargs={"app_label": "cms"}) in response.content.decode()

    def test_cms_usersettings_hides_history_action(self, admin_client):
        response = admin_client.get("/admin/cms/usersettings/")
        assert response.status_code == 200
        assert '<span class="material-symbols-outlined">\n                history\n            </span>' not in response.content.decode()
