from __future__ import annotations

import re
from typing import Mapping, Any

from django.conf import settings
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

# accept any CSS color function; pass-through unchanged
_FUNC_PREFIXES = ("oklch(", "lab(", "lch(", "rgb(", "rgba(", "hsl(", "hsla(", "color(", "var(")
_RGB_COMMA = re.compile(r"^\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*$")
_RGB_SPACE = re.compile(r"^\s*\d{1,3}\s+\d{1,3}\s+\d{1,3}\s*$")

def _to_css_value(v) -> str:
    s = str(v).strip()
    if s.startswith(_FUNC_PREFIXES) or s.startswith("#"):  # color function or hex → already valid
        return s
    # legacy palettes like "249, 250, 251" or "249 250 251"
    if _RGB_COMMA.match(s):
        return f"rgb({s})"
    if _RGB_SPACE.match(s):
        r, g, b = re.split(r"\s+", s)
        return f"rgb({r}, {g}, {b})"
    return s  # named colors etc.

@register.simple_tag
def unfold_theme_colors() -> str:
    """
    Emit the same custom properties Unfold injects in admin, but for the frontend.
    Works with OKLCH palettes (preferred) or older rgb triplets.
    """
    colors = (getattr(settings, "UNFOLD", {}) or {}).get("COLORS") or {}
    if not colors:
        return ""

    out = ['<style id="unfold-theme-colors">', ":root {"]
    for group, mapping in colors.items():
        if not isinstance(mapping, dict):
            continue
        if group == "font":
            for name, val in mapping.items():
                out.append(f"  --color-font-{name}: {_to_css_value(val)};")
            continue
        # base/primary/... with numeric shades
        try:
            items = sorted(mapping.items(), key=lambda kv: int(kv[0]))
        except Exception:
            items = mapping.items()
        for shade, val in items:
            out.append(f"  --color-{group}-{shade}: {_to_css_value(val)};")
    out += ["}", "</style>"]
    return mark_safe("\n".join(out))

@register.simple_tag(takes_context=True)
def unfold_extra_styles(context) -> str:
    """
    Load Unfolds extra stylesheet and adds theme colors from settings.UNFOLD['COLORS'].
    """
    if not (context.get("user") and context["user"].is_authenticated):
        return ""

    link_tag = f'<link rel="stylesheet" type="text/css" href="{static("unfold_extra/css/styles.css")}">'
    theme_style = unfold_theme_colors()
    html = f"{link_tag}\n{theme_style}" if theme_style else link_tag
    return mark_safe(html)

@register.simple_tag(takes_context=True)
def unfold_extra_theme_sync(context) -> str:
    """
    Load a custom theme receiver script to switch django cm theme from unfolding when encapsulated in an iframe.
    """
    if not (context.get("user") and context["user"].is_authenticated):
        return ""

    src = static("unfold_extra/js/theme-sync.js")
    return mark_safe(f'<script src="{src}"></script>')