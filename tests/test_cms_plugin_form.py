"""Plugin forms must get Unfold's labels even when no Unfold admin page ran first.

Unfold swaps its ``AdminForm``/``Fieldline`` into ``django.contrib.admin.helpers``
only in ``ModelAdmin.changeform_view``, which ``UnfoldCMSPluginBase`` doesn't inherit.
A plugin modal opened first in a fresh process got Django's labels — a trailing
colon, and checkbox labels shifted by the ``-ml-2`` their row expects to cancel (#3).
"""

import pytest
from django.contrib.admin import helpers
from unfold import forms as unfold_forms

from tests.visual.data import cms_page_create, cms_plugins_create


@pytest.mark.django_db
class TestPluginFormLabels:
    @pytest.fixture
    def plugin_form(self, admin_client, django_user_model, monkeypatch):
        # a fresh process: Django's own helpers, as before any Unfold change form
        monkeypatch.setattr(helpers, "AdminForm", unfold_forms.BaseAdminForm)
        monkeypatch.setattr(helpers, "Fieldline", unfold_forms.BaseFieldline)
        content = cms_page_create(title="Home", user=django_user_model.objects.get())
        hero, _ = cms_plugins_create(page_content=content)

        response = admin_client.get(f"/admin/cms/placeholder/edit-plugin/{hero.pk}/")

        assert response.status_code == 200
        return response.content.decode()

    def test_checkbox_label_gets_unfold_classes(self, plugin_form):
        assert '<label class="font-semibold ml-2 ' in plugin_form
        assert 'class="vCheckboxLabel" for="id_is_highlighted"' not in plugin_form

    def test_labels_have_no_django_suffix(self, plugin_form):
        assert 'for="id_cta_label">CTA label<' in plugin_form
