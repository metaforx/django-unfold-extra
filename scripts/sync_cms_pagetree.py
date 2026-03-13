#!/usr/bin/env python3
"""
Sync cms.pagetree.css from the installed django-cms package and apply
Unfold compatibility patches.

Usage:
    poetry run python scripts/sync_cms_pagetree.py

What it does:
    1. Locates the installed django-cms static CSS
    2. Copies cms.pagetree.css to unfold_extra/static/unfold_extra/cms/css/
    3. Applies patches for Unfold compatibility:
       - Removes bare `.hidden` from `.cms-hidden, .hidden` rule
         (conflicts with Tailwind's `.hidden` utility used by Unfold sidebar)
    4. Prints the CMS version and a summary of changes

After running, review the diff and commit the updated file.
"""

import importlib
import re
import sys
from pathlib import Path

DEST = Path(__file__).resolve().parent.parent / "unfold_extra" / "static" / "unfold_extra" / "cms" / "css" / "cms.pagetree.css"

PATCHES = [
    # (description, search, replace)
    (
        "Remove bare .hidden selector (conflicts with Tailwind/Unfold sidebar)",
        ".cms-hidden,.hidden{display:none!important}",
        ".cms-hidden{display:none!important}",
    ),
]

# CMS CSS lives at cms/css/<version>/cms.pagetree.css and uses relative paths
# like ../../fonts/<version>/ and ../../img/pagetree/. Our vendored copy lives
# at unfold_extra/cms/css/cms.pagetree.css, so we rewrite those paths to
# absolute /static/cms/ references.
FONT_PATH_RE = re.compile(r'url\((\.\./\.\./)(?=fonts/|img/)')
FONT_PATH_REPLACE = "url(/static/cms/"


def find_cms_pagetree_css() -> Path:
    """Locate cms.pagetree.css from the installed django-cms package."""
    try:
        cms = importlib.import_module("cms")
    except ImportError:
        print("ERROR: django-cms is not installed. Install it first:", file=sys.stderr)
        print("  poetry install", file=sys.stderr)
        sys.exit(1)

    cms_static = Path(cms.__file__).parent / "static" / "cms" / "css"
    # CMS versions its static files in subdirs (e.g. 5.0.3/)
    candidates = list(cms_static.glob("*/cms.pagetree.css"))
    if not candidates:
        # fallback: maybe it's directly in css/
        direct = cms_static / "cms.pagetree.css"
        if direct.exists():
            return direct
        print(f"ERROR: cms.pagetree.css not found under {cms_static}", file=sys.stderr)
        sys.exit(1)

    # Use the latest version by semantic version, not lexicographic order
    def _version_key(p: Path):
        parts = p.parent.name.split(".")
        try:
            return tuple(int(x) for x in parts)
        except ValueError:
            return (0,)

    source = max(candidates, key=_version_key)
    return source


def main():
    source = find_cms_pagetree_css()
    version_dir = source.parent.name  # e.g. "5.0.3"
    print(f"Source: {source}")
    print(f"CMS static version: {version_dir}")

    css = source.read_text()
    original = css

    for desc, search, replace in PATCHES:
        if search in css:
            css = css.replace(search, replace)
            print(f"  PATCHED: {desc}")
        else:
            # Try with spaces (in case of unminified CSS)
            search_spaced = search.replace(",", ", ").replace("{", " { ").replace("}", " }").replace("!important", " !important")
            if search_spaced in css:
                css = css.replace(search_spaced, replace.replace(",", ", ").replace("{", " { ").replace("}", " }").replace("!important", " !important"))
                print(f"  PATCHED: {desc}")
            else:
                print(f"  WARNING: patch target not found — {desc}")
                print(f"           Expected: {search}")
                print(f"           CSS may have changed in this CMS version. Manual review needed.")

    # Rewrite relative asset paths to absolute /static/cms/ paths
    count = len(FONT_PATH_RE.findall(css))
    if count:
        css = FONT_PATH_RE.sub(FONT_PATH_REPLACE, css)
        print(f"  PATCHED: Rewrote {count} relative asset paths to /static/cms/")
    else:
        print("  WARNING: no relative asset paths found — font/image URLs may need manual review")

    if css == original:
        print("\nNo patches were applied. CSS may have changed upstream.")

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(css)
    print(f"\nWritten to: {DEST}")
    print(f"File size: {len(css):,} bytes")
    print("\nDone. Review with: git diff unfold_extra/static/unfold_extra/cms/css/cms.pagetree.css")


if __name__ == "__main__":
    main()
