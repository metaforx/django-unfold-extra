import pytest
from django.contrib.sites.models import Site
from django.test import RequestFactory


@pytest.mark.django_db
class TestAdminSiteCompat:
    """django-cms 5.1 removed cms.admin.pageadmin.get_site; unfold_extra falls back to
    cms.utils.get_current_site, which gained the request argument in the same release."""

    def test_resolves_a_site_for_a_plain_request(self):
        from unfold_extra.contrib.cms.utils import _get_admin_site

        request = RequestFactory().get("/admin/")
        request.session = {}

        assert _get_admin_site(request).pk == Site.objects.get_current().pk

    def test_language_from_request_uses_it(self):
        from unfold_extra.contrib.cms.utils import _language_from_request

        request = RequestFactory().get("/admin/", {"language": "de"})
        request.session = {}

        assert _language_from_request(request) == "de"
