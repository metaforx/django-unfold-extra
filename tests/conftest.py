import pytest
from django.contrib.auth import get_user_model

# Names of reference images rewritten this session, reported in the terminal summary.
UPDATED_SNAPSHOTS = pytest.StashKey[list]()


def pytest_addoption(parser):
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="Overwrite visual reference images with the current rendering.",
    )


def pytest_configure(config):
    config.stash[UPDATED_SNAPSHOTS] = []


def pytest_terminal_summary(terminalreporter):
    updated = terminalreporter.config.stash.get(UPDATED_SNAPSHOTS, [])
    if not updated:
        return
    terminalreporter.write_sep("-", "updated snapshot references")
    for name in sorted(updated):
        terminalreporter.write_line(f"  {name}")
    terminalreporter.write_line("Review these images before committing them.")


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


def admin_login(*, context, live_server, username: str, password: str):
    """Log a browser context in through the real admin login form and return the page."""
    page = context.new_page()
    page.goto(f"{live_server.url}/admin/login/?next=/admin/")
    page.fill("#id_username", username)
    page.fill("#id_password", password)
    page.click("[type=submit]")
    page.wait_for_load_state("networkidle")
    return page


@pytest.fixture(scope="function")
def authenticated_page(browser, live_server, admin_user):
    """Playwright page authenticated as admin via the Django login form."""
    context = browser.new_context()
    page = admin_login(
        context=context,
        live_server=live_server,
        username="testadmin",
        password="testpass",
    )
    yield page
    context.close()
