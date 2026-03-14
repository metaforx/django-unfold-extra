import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def admin_client(client, django_user_model):
    """A Django test client logged in as an admin user."""
    user = django_user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password",
    )
    client.force_login(user)
    return client


@pytest.fixture(scope="function")
def admin_user(db):
    """Create an admin user."""
    User = get_user_model()
    return User.objects.create_superuser(
        username="testadmin",
        email="testadmin@example.com",
        password="testpass",
    )


@pytest.fixture(scope="function")
def authenticated_page(browser, live_server, admin_user):
    """Playwright page authenticated as admin via the Django login form."""
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{live_server.url}/admin/login/?next=/admin/")
    page.fill("#id_username", "testadmin")
    page.fill("#id_password", "testpass")
    page.click("[type=submit]")
    page.wait_for_load_state("networkidle")
    yield page
    context.close()
