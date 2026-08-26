#!/usr/bin/env python3
"""
Sync admin_filer.css from the installed django-filer package and apply
Unfold compatibility patches.

Usage:
    uv run python scripts/sync_filer_css.py

What it does:
    1. Locates the installed django-filer static CSS
    2. Copies admin_filer.css to unfold_extra/contrib/filer/static/filer/css/,
       deliberately shadowing filer's own `filer/css/admin_filer.css` static path.
       Because `unfold_extra.contrib.filer` is listed before `filer` in
       INSTALLED_APPS, this patched copy wins for every
       `{% static 'filer/css/admin_filer.css' %}` reference in filer's admin
       templates (base_site, change_form, delete_confirmation, choose_* ...),
       so we don't have to override each of those templates individually.
    3. Applies patches for Unfold compatibility:
       - Removes the bare `.hidden{display:none!important}` rule
         (conflicts with Tailwind's `.hidden` utility used by the Unfold sidebar
         — same class of issue handled by scripts/sync_cms_pagetree.py)
       - Drops `height:100% !important` from the global `html,body` rule
         (the !important fights Unfold's flex layout)
    4. Prints the filer version and a summary of changes

admin_filer.css only references inline `data:` URIs, so — unlike the CMS
pagetree CSS — there are no relative font/image paths to rewrite, which is
what makes same-path shadowing safe here.

After running, review the diff and commit the updated file.
"""

import importlib
import sys
from pathlib import Path

# Shadow filer's own static path so every `{% static 'filer/css/admin_filer.css' %}`
# in filer's admin templates resolves to this patched copy (contrib.filer is before
# filer in INSTALLED_APPS, so the staticfiles finder returns it first).
DEST = (
    Path(__file__).resolve().parent.parent
    / "unfold_extra"
    / "contrib"
    / "filer"
    / "static"
    / "filer"
    / "css"
    / "admin_filer.css"
)

HEADER = (
    "/* Vendored from django-filer and patched for Unfold compatibility by\n"
    "   scripts/sync_filer_css.py. DO NOT EDIT BY HAND. This file deliberately\n"
    "   shadows filer's own filer/css/admin_filer.css static path (contrib.filer\n"
    "   is before filer in INSTALLED_APPS). Re-run the script after upgrading\n"
    "   django-filer. */\n"
)

PATCHES = [
    # (description, search, replace)
    (
        "Remove bare .hidden selector (conflicts with Tailwind/Unfold sidebar)",
        "}.hidden{display:none !important}",
        "}",
    ),
    (
        "Drop height:100% !important from global html,body rule",
        "html,body{min-width:320px;height:100% !important}",
        "html,body{min-width:320px}",
    ),
    (
        # filer lays its file/image widget out under `form .form-row .filer-dropzone`,
        # a scope it assumes only Django's own change form provides — but Unfold puts
        # `form-row` on every fieldset row too (`fieldset_row_classes`), so the whole
        # block applies and misfires: `.filerFile` is `position: absolute` inside a box
        # that is only as tall as the `min-height` below, so the file name, filer's
        # buttons and the drop hint spill out over the next field, where they cover its
        # controls. Rename the scope to something no page renders; unfold_extra lays the
        # widget out with flex instead (see the "django-filer file/image widget" block
        # in unfold_extra/src/css/unfold_extra.css).
        "Neutralize filer's absolute/float widget layout (Unfold rows are .form-row too)",
        "form .form-row .filer-dropzone",
        "form .filer-legacy-form-row .filer-dropzone",
    ),
    (
        # ... and drop the `!important` from the one widget rule filer leaves unscoped,
        # so the flex layout can size the box by its content.
        "Drop !important from .filer-dropzone min-height",
        ".filer-dropzone{min-height:100px !important}",
        ".filer-dropzone{min-height:100px}",
    ),
    (
        # The `filebrowser` body class on the directory-listing view scopes this rule
        # over the *whole* page, including Unfold's sidebar — whose navigation group
        # titles are <h2> elements that also act as the collapse toggle. Hiding them
        # makes the entire sidebar appear empty. Re-scope to filer's #content area so
        # it still hides filer's own placeholder content heading but leaves the
        # sidebar untouched.
        "Scope .filebrowser h2 hide rule to #content (keeps Unfold sidebar titles)",
        ".filebrowser h2{display:none}",
        ".filebrowser #content h2{display:none}",
    ),
]


def find_admin_filer_css() -> Path:
    """Locate admin_filer.css from the installed django-filer package."""
    try:
        filer = importlib.import_module("filer")
    except ImportError:
        print("ERROR: django-filer is not installed. Install it first:", file=sys.stderr)
        print("  uv sync  (or: pip install django-unfold-extra[filer])", file=sys.stderr)
        sys.exit(1)

    source = Path(filer.__file__).parent / "static" / "filer" / "css" / "admin_filer.css"
    if not source.exists():
        print(f"ERROR: admin_filer.css not found at {source}", file=sys.stderr)
        sys.exit(1)
    return source


def main():
    source = find_admin_filer_css()
    filer = importlib.import_module("filer")
    print(f"Source: {source}")
    print(f"filer version: {getattr(filer, '__version__', 'unknown')}")

    css = source.read_text()
    original = css

    for desc, search, replace in PATCHES:
        if search in css:
            css = css.replace(search, replace)
            print(f"  PATCHED: {desc}")
        else:
            print(f"  WARNING: patch target not found — {desc}")
            print(f"           Expected: {search}")
            print("           CSS may have changed in this filer version. Manual review needed.")

    if css == original:
        print("\nNo patches were applied. CSS may have changed upstream.")

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(HEADER + css)
    print(f"\nWritten to: {DEST}")
    print(f"File size: {len(css):,} bytes")
    print(f"\nDone. Review with: git diff {DEST.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
