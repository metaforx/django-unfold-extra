"""The ``assert_snapshot`` fixture's three cases: missing, mismatch, update.

The reference and results directories are redirected to ``tmp_path`` by overriding the
fixtures they come from, so these tests never touch the committed snapshots.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from tests.conftest import UPDATED_SNAPSHOTS


@pytest.fixture(autouse=True)
def isolated_update_record(pytestconfig):
    """Keep these tests out of the real run's "updated references" summary."""
    original = pytestconfig.stash[UPDATED_SNAPSHOTS]
    pytestconfig.stash[UPDATED_SNAPSHOTS] = []
    yield
    pytestconfig.stash[UPDATED_SNAPSHOTS] = original


@pytest.fixture
def snapshots_dir(tmp_path) -> Path:
    return tmp_path / "snapshots"


@pytest.fixture
def results_dir(tmp_path) -> Path:
    return tmp_path / "results"


def _png(*, color: tuple[int, int, int] = (255, 255, 255), size: tuple[int, int] = (60, 40)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "PNG")
    return buffer.getvalue()


def _update_snapshots(*, pytestconfig, monkeypatch, enabled: bool) -> None:
    monkeypatch.setattr(pytestconfig.option, "update_snapshots", enabled)


class TestMissingReference:
    def test_writes_the_reference_and_fails(self, assert_snapshot, snapshots_dir):
        with pytest.raises(pytest.fail.Exception, match="no reference image"):
            assert_snapshot(_png(), "admin-index--light")

        assert (snapshots_dir / "admin-index--light.png").exists()

    def test_with_update_writes_and_passes(
        self, assert_snapshot, snapshots_dir, pytestconfig, monkeypatch
    ):
        _update_snapshots(pytestconfig=pytestconfig, monkeypatch=monkeypatch, enabled=True)

        assert_snapshot(_png(), "admin-index--dark")

        assert (snapshots_dir / "admin-index--dark.png").exists()
        assert "admin-index--dark" in pytestconfig.stash[UPDATED_SNAPSHOTS]


class TestExistingReference:
    def test_identical_rendering_passes(self, assert_snapshot, snapshots_dir):
        snapshots_dir.mkdir(parents=True)
        (snapshots_dir / "login--light.png").write_bytes(_png())

        assert_snapshot(_png(), "login--light")

    def test_mismatch_fails_and_writes_the_triplet(self, assert_snapshot, snapshots_dir, results_dir):
        snapshots_dir.mkdir(parents=True)
        (snapshots_dir / "login--dark.png").write_bytes(_png())

        with pytest.raises(pytest.fail.Exception, match="of pixels differ"):
            assert_snapshot(_png(color=(0, 0, 0)), "login--dark")

        assert sorted(path.name for path in results_dir.iterdir()) == [
            "login--dark.actual.png",
            "login--dark.diff.png",
            "login--dark.expected.png",
        ]

    def test_size_change_fails(self, assert_snapshot, snapshots_dir, results_dir):
        snapshots_dir.mkdir(parents=True)
        (snapshots_dir / "filer-root--light.png").write_bytes(_png())

        with pytest.raises(pytest.fail.Exception, match="size changed"):
            assert_snapshot(_png(size=(60, 80)), "filer-root--light")

        assert (results_dir / "filer-root--light.actual.png").exists()

    def test_update_overwrites_and_records(
        self, assert_snapshot, snapshots_dir, pytestconfig, monkeypatch
    ):
        snapshots_dir.mkdir(parents=True)
        reference = snapshots_dir / "article-changelist--light.png"
        reference.write_bytes(_png())
        _update_snapshots(pytestconfig=pytestconfig, monkeypatch=monkeypatch, enabled=True)

        assert_snapshot(_png(color=(0, 0, 0)), "article-changelist--light")

        assert Image.open(reference).getpixel((0, 0)) == (0, 0, 0)
        assert "article-changelist--light" in pytestconfig.stash[UPDATED_SNAPSHOTS]

    def test_rerun_without_update_passes_after_an_update(
        self, assert_snapshot, snapshots_dir, pytestconfig, monkeypatch
    ):
        snapshots_dir.mkdir(parents=True)
        (snapshots_dir / "cms-pagetree--dark.png").write_bytes(_png())
        _update_snapshots(pytestconfig=pytestconfig, monkeypatch=monkeypatch, enabled=True)
        assert_snapshot(_png(color=(0, 0, 0)), "cms-pagetree--dark")

        _update_snapshots(pytestconfig=pytestconfig, monkeypatch=monkeypatch, enabled=False)
        assert_snapshot(_png(color=(0, 0, 0)), "cms-pagetree--dark")
