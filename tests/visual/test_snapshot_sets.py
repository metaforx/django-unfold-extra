"""One reference set per supported django CMS version, picked from the installed one."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from tests.conftest import installed_cms_minor

from .conftest import SNAPSHOTS_ROOT, snapshot_set_dir, snapshot_set_error
from .views import VIEWS


def test_set_dir_is_per_minor_version(tmp_path):
    assert snapshot_set_dir(root=tmp_path, cms_version="5.1") == tmp_path / "cms-5.1"


def test_snapshots_dir_follows_installed_version(snapshots_dir: Path):
    assert snapshots_dir == SNAPSHOTS_ROOT / f"cms-{installed_cms_minor()}"


def test_existing_set_can_run(tmp_path):
    (tmp_path / "cms-5.1").mkdir()
    assert snapshot_set_error(root=tmp_path, cms_version="5.1") is None


def test_missing_set_names_installed_and_available(tmp_path):
    (tmp_path / "cms-5.0").mkdir()
    (tmp_path / "cms-5.1").mkdir()
    error = snapshot_set_error(root=tmp_path, cms_version="5.2")
    assert error is not None
    assert "django CMS 5.2 (installed)" in error
    assert "available sets: cms-5.0, cms-5.1" in error


def test_every_supported_version_has_a_set():
    """Supported versions are the ``cmsXY`` dependency groups in pyproject.toml."""
    pyproject = tomllib.loads((Path(__file__).parents[2] / "pyproject.toml").read_text())
    groups = pyproject["dependency-groups"]
    supported = sorted(f"{m[1]}.{m[2]}" for g in groups if (m := re.fullmatch(r"cms(\d)(\d+)", g)))
    assert supported, "no cmsXY dependency groups in pyproject.toml"
    for cms_version in supported:
        assert snapshot_set_dir(root=SNAPSHOTS_ROOT, cms_version=cms_version).is_dir(), cms_version


def test_every_set_covers_every_view_and_theme():
    expected = {f"{view.name}--{theme}.png" for view in VIEWS for theme in ("light", "dark")}
    sets = sorted(path for path in SNAPSHOTS_ROOT.glob("cms-*") if path.is_dir())
    assert sets, f"no reference sets under {SNAPSHOTS_ROOT}"
    for reference_set in sets:
        present = {path.name for path in reference_set.glob("*.png")}
        assert present == expected, (
            f"{reference_set.name}: missing {sorted(expected - present)}, extra {sorted(present - expected)}"
        )
