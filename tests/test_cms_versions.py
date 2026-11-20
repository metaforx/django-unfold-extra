"""The ``requires_cms`` marker: version-specific tests are skipped with a reason, never deleted."""

import pytest

from tests.conftest import cms_skip_reason, installed_cms_minor


class TestCmsSkipReason:
    def test_runs_on_a_listed_version(self):
        assert cms_skip_reason(required=("5.1",), installed="5.1") is None

    def test_skip_reason_names_required_and_installed(self):
        assert cms_skip_reason(required=("5.1",), installed="5.0") == (
            "requires django CMS 5.1 (installed: 5.0)"
        )

    def test_several_versions(self):
        assert cms_skip_reason(required=("5.0", "5.1"), installed="5.0") is None


def test_installed_version_is_major_minor():
    assert installed_cms_minor().count(".") == 1


@pytest.mark.requires_cms("5.1")
def test_marker_runs_only_on_django_cms_5_1():
    assert installed_cms_minor() == "5.1"
