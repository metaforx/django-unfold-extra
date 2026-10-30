"""The registry itself must stay well-formed.

Names become snapshot file stems and pytest ids, so a duplicate would silently make
two views share one reference image.
"""

from __future__ import annotations

import re
from collections import Counter

from .views import VIEWS

KEBAB_CASE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def test_names_are_unique():
    duplicates = [name for name, count in Counter(view.name for view in VIEWS).items() if count > 1]
    assert not duplicates, f"duplicate view names: {', '.join(sorted(duplicates))}"


def test_names_are_kebab_case():
    invalid = [view.name for view in VIEWS if not KEBAB_CASE.match(view.name)]
    assert not invalid, f"view names must be kebab-case: {', '.join(sorted(invalid))}"
