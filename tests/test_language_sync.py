import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestCmsSetLanguageView:
    """Verify that cms_set_language view syncs language into CMS UserSettings
    and redirects correctly in both directions (en→de, de→en)."""

    def test_set_language_updates_cms_user_settings(self, admin_client, django_user_model):
        from cms.models import UserSettings

        user = django_user_model.objects.get(username="admin")
        UserSettings.objects.get_or_create(user=user, defaults={"language": "en"})

        admin_client.post(reverse("set_language"), {"language": "de", "next": "/admin/"})

        assert UserSettings.objects.get(user=user).language == "de"

    def test_creates_user_settings_if_missing(self, admin_client, django_user_model):
        """update_or_create should create UserSettings when no row exists."""
        from cms.models import UserSettings

        user = django_user_model.objects.get(username="admin")
        assert not UserSettings.objects.filter(user=user).exists()

        admin_client.post(reverse("set_language"), {"language": "de", "next": "/admin/"})

        assert UserSettings.objects.get(user=user).language == "de"

    def test_redirect_en_to_de(self, admin_client):
        """en→de: /admin/ should redirect to /de/admin/."""
        response = admin_client.post(
            reverse("set_language"), {"language": "de", "next": "/admin/"}
        )
        assert response.status_code == 302
        assert response.url == "/de/admin/"

    def test_redirect_de_to_en_with_referer(self, admin_client):
        """de→en via Unfold's empty-next form: should redirect to /admin/.

        This is the critical test. Unfold's language form sends next="" and
        set_language falls back to HTTP_REFERER. With prefix_default_language=False,
        LocaleMiddleware forces LANGUAGE_CODE for non-prefixed URLs, so
        cms_set_language must re-activate the cookie language for translate_url
        to resolve the German-prefixed referer correctly.
        """
        # First switch to German so the cookie is "de"
        admin_client.post(reverse("set_language"), {"language": "de", "next": "/admin/"})

        # Switch back, simulating Unfold's empty next + referer
        response = admin_client.post(
            reverse("set_language"),
            {"language": "en", "next": ""},
            HTTP_REFERER="http://testserver/de/admin/",
        )
        assert response.status_code == 302
        assert response.url == "http://testserver/admin/"

    def test_cookie_roundtrip(self, admin_client):
        """Cookie is set correctly in both directions."""
        r1 = admin_client.post(
            reverse("set_language"), {"language": "de", "next": "/admin/"}
        )
        assert r1.cookies["django_language"].value == "de"

        r2 = admin_client.post(
            reverse("set_language"), {"language": "en", "next": "/de/admin/"}
        )
        assert r2.cookies["django_language"].value == "en"
