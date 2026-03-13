"""Smoke tests to verify test infrastructure, CMS, and unfold_extra are working."""

import pytest
from django.contrib.admin.sites import site as admin_site

from testapp.models import Article, Category, SimpleModel


@pytest.mark.django_db
class TestModelsExist:
    """Verify all test models are properly defined and can be instantiated."""

    def test_simple_model(self):
        obj = SimpleModel.objects.create(name="Test")
        assert str(obj) == "Test"

    def test_category_translatable(self):
        cat = Category()
        cat.set_current_language("en")
        cat.name = "Fiction"
        cat.save()
        assert str(cat) == "Fiction"

    def test_article_translatable(self):
        article = Article()
        article.set_current_language("en")
        article.title = "Hello World"
        article.save()
        assert str(article) == "Hello World"

    def test_article_with_category(self):
        cat = Category()
        cat.set_current_language("en")
        cat.name = "News"
        cat.save()
        article = Article(category=cat)
        article.set_current_language("en")
        article.title = "Breaking"
        article.save()
        assert article.category == cat


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


@pytest.mark.django_db
class TestCMSAdminAccess:
    """Verify CMS admin pages work with unfold_extra re-registration."""

    def test_page_content_changelist(self, admin_client):
        response = admin_client.get("/admin/cms/pagecontent/")
        assert response.status_code == 200

    def test_page_changelist_redirects_to_pagecontent(self, admin_client):
        """CMS Page changelist redirects to PageContent changelist."""
        response = admin_client.get("/admin/cms/page/")
        assert response.status_code == 302
        assert "/admin/cms/pagecontent/" in response.url


@pytest.mark.django_db
class TestUnfoldExtraApps:
    """Verify unfold_extra apps are loaded."""

    def test_unfold_extra_app_loaded(self):
        from django.apps import apps

        assert apps.is_installed("unfold_extra")

    def test_unfold_extra_cms_app_loaded(self):
        from django.apps import apps

        assert apps.is_installed("unfold_extra.contrib.cms")

    def test_unfold_extra_parler_app_loaded(self):
        from django.apps import apps

        assert apps.is_installed("unfold_extra.contrib.parler")

    def test_unfold_extra_auth_app_loaded(self):
        from django.apps import apps

        assert apps.is_installed("unfold_extra.contrib.auth")

    def test_unfold_extra_sites_app_loaded(self):
        from django.apps import apps

        assert apps.is_installed("unfold_extra.contrib.sites")
