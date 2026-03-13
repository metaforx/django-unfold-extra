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
