from django.template.loader import render_to_string
from django.urls import NoReverseMatch
from django.utils.functional import Promise


def patch_unfold_header_title() -> None:
    """
    Patch unfold's header_title tag so missing admin app_list URLs for
    plugin-only app labels do not crash admin pages.
    """
    from unfold.templatetags import unfold as unfold_tags

    if getattr(unfold_tags, "_unfold_extra_header_title_patched", False):
        return

    original_header_title = unfold_tags.header_title

    def safe_header_title(context):
        # A lazy translation as ``original`` is neither a ``str`` nor a model, so
        # Unfold's ``original._meta`` lookup blows up. Coerce it to a real string.
        original = context.get("original")
        if isinstance(original, Promise):
            with context.push(original=str(original)):
                return safe_header_title(context)
        try:
            return original_header_title(context)
        except NoReverseMatch:
            title = context.get("title")
            if not title:
                return ""
            return render_to_string(
                "unfold/helpers/header_title.html",
                request=context.request,
                context={"parts": [{"title": title}]},
            )

    unfold_tags.header_title = safe_header_title
    unfold_tags.register.simple_tag(name="header_title", takes_context=True)(
        safe_header_title
    )
    unfold_tags._unfold_extra_header_title_patched = True
