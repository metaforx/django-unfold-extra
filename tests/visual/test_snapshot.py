"""The snapshot engine decides whether a screenshot changed — so it gets its own tests.

Unmarked on purpose: these are pure image maths with no browser and no database, so
they run in the default suite and in CI.
"""

from __future__ import annotations

from PIL import Image

from .snapshot import snapshot_compare, snapshot_write_results

SIZE = (100, 100)
TOTAL_PIXELS = SIZE[0] * SIZE[1]


def _image(*, color: tuple[int, int, int] = (255, 255, 255), size: tuple[int, int] = SIZE) -> Image.Image:
    return Image.new("RGB", size, color)


def _with_differing_pixels(*, count: int) -> Image.Image:
    image = _image()
    for index in range(count):
        image.putpixel((index % SIZE[0], index // SIZE[0]), (0, 0, 0))
    return image


class TestSnapshotCompare:
    def test_identical_images_pass(self):
        result = snapshot_compare(expected=_image(), actual=_image())

        assert result.passed
        assert result.diff_ratio == 0
        assert result.diff_image is None

    def test_difference_within_tolerance_passes(self):
        # 1 pixel in 10 000 is exactly the 0.01 % default ceiling.
        result = snapshot_compare(expected=_image(), actual=_with_differing_pixels(count=1))

        assert result.passed
        assert result.diff_ratio == 1 / TOTAL_PIXELS
        assert result.diff_image is None

    def test_difference_above_tolerance_fails(self):
        result = snapshot_compare(expected=_image(), actual=_with_differing_pixels(count=50))

        assert not result.passed
        assert result.diff_ratio == 50 / TOTAL_PIXELS
        assert result.diff_image is not None
        assert result.diff_image.size == SIZE
        assert "0.5000%" in result.summary

    def test_size_mismatch_is_reported_separately(self):
        result = snapshot_compare(expected=_image(), actual=_image(size=(100, 120)))

        assert not result.passed
        assert result.size_mismatch
        assert result.expected_size == (100, 100)
        assert result.actual_size == (100, 120)
        assert result.diff_image is None
        assert "size changed" in result.summary

    def test_max_diff_ratio_is_configurable(self):
        actual = _with_differing_pixels(count=50)

        assert snapshot_compare(expected=_image(), actual=actual, max_diff_ratio=0.01).passed
        assert not snapshot_compare(expected=_image(), actual=actual, max_diff_ratio=0.0).passed


class TestSnapshotWriteResults:
    def test_writes_the_failure_triplet(self, tmp_path):
        result = snapshot_compare(expected=_image(), actual=_with_differing_pixels(count=50))

        written = snapshot_write_results(name="admin-index--dark", result=result, results_dir=tmp_path)

        assert [path.name for path in written] == [
            "admin-index--dark.expected.png",
            "admin-index--dark.actual.png",
            "admin-index--dark.diff.png",
        ]
        assert all(path.exists() for path in written)

    def test_size_mismatch_writes_no_diff(self, tmp_path):
        result = snapshot_compare(expected=_image(), actual=_image(size=(100, 120)))

        written = snapshot_write_results(name="filer-root--light", result=result, results_dir=tmp_path)

        assert [path.name for path in written] == [
            "filer-root--light.expected.png",
            "filer-root--light.actual.png",
        ]

    def test_creates_the_results_directory(self, tmp_path):
        result = snapshot_compare(expected=_image(), actual=_with_differing_pixels(count=50))
        results_dir = tmp_path / "results"

        snapshot_write_results(name="login--light", result=result, results_dir=results_dir)

        assert results_dir.is_dir()
