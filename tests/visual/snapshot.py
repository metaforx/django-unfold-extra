"""Screenshot comparison: two PNGs in, a verdict and a diff image out.

Deliberately free of pytest imports — the fixture in ``conftest.py`` owns the test
lifecycle, this module owns the pixels.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from pixelmatch import pixelmatch

# Per-pixel YIQ delta before a pixel counts as different.
DEFAULT_THRESHOLD = 0.1
# Share of differing pixels a screenshot may still pass with (0.01 %).
DEFAULT_MAX_DIFF_RATIO = 0.0001


@dataclass(frozen=True)
class SnapshotResult:
    passed: bool
    diff_ratio: float
    actual_image: Image.Image
    expected_image: Image.Image | None = None
    diff_image: Image.Image | None = None
    size_mismatch: bool = False

    @property
    def expected_size(self) -> tuple[int, int] | None:
        return self.expected_image.size if self.expected_image else None

    @property
    def actual_size(self) -> tuple[int, int]:
        return self.actual_image.size

    @property
    def summary(self) -> str:
        if self.size_mismatch:
            return f"size changed: expected {self.expected_size}, got {self.actual_size}"
        return f"{self.diff_ratio:.4%} of pixels differ"


def snapshot_compare(
    *,
    expected: Image.Image,
    actual: Image.Image,
    threshold: float = DEFAULT_THRESHOLD,
    max_diff_ratio: float = DEFAULT_MAX_DIFF_RATIO,
) -> SnapshotResult:
    """Compare two images pixel by pixel.

    A size change is reported on its own: pixelmatch needs equal dimensions, and a page
    that grew or shrank is a visual change in itself.
    """
    expected_rgba = expected.convert("RGBA")
    actual_rgba = actual.convert("RGBA")

    if expected_rgba.size != actual_rgba.size:
        return SnapshotResult(
            passed=False,
            diff_ratio=1.0,
            actual_image=actual_rgba,
            expected_image=expected_rgba,
            size_mismatch=True,
        )

    width, height = expected_rgba.size
    diff_data = [0] * (width * height * 4)
    differing = pixelmatch(
        list(expected_rgba.tobytes()),
        list(actual_rgba.tobytes()),
        width,
        height,
        diff_data,
        threshold=threshold,
    )

    diff_ratio = differing / (width * height) if width and height else 0.0
    passed = diff_ratio <= max_diff_ratio
    diff_image = None
    if not passed:
        diff_image = Image.frombytes("RGBA", (width, height), bytes(bytearray(diff_data)))

    return SnapshotResult(
        passed=passed,
        diff_ratio=diff_ratio,
        actual_image=actual_rgba,
        expected_image=expected_rgba,
        diff_image=diff_image,
    )


def snapshot_write_results(*, name: str, result: SnapshotResult, results_dir: Path) -> list[Path]:
    """Write the failure triplet and return the files written, in that order."""
    results_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    if result.expected_image is not None:
        expected_path = results_dir / f"{name}.expected.png"
        result.expected_image.save(expected_path)
        written.append(expected_path)

    actual_path = results_dir / f"{name}.actual.png"
    result.actual_image.save(actual_path)
    written.append(actual_path)

    if result.diff_image is not None:
        diff_path = results_dir / f"{name}.diff.png"
        result.diff_image.save(diff_path)
        written.append(diff_path)

    return written
