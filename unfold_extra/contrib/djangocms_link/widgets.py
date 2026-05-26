from copy import deepcopy

from djangocms_link.fields import (
    LinkAutoCompleteWidget,
    LinkFormField,
    LinkWidget,
)
from unfold.widgets import (
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminURLInputWidget,
)


class UnfoldLinkAutoCompleteWidget(LinkAutoCompleteWidget):
    """
    Keep djangocms_link autocomplete behavior.
    Only adapt attrs/media for Unfold.
    """

    class Media:
        extra = ""
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "unfold/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)

        existing = attrs.get("class", "").split()
        wanted = ["unfold-admin-autocomplete", "admin-autocomplete"]

        attrs["class"] = " ".join(cls for cls in [*wanted, *existing] if cls)
        attrs["data-theme"] = "admin-autocomplete"

        return attrs


class UnfoldLinkWidget(LinkWidget):
    def __init__(self, site_selector=None):
        super().__init__(site_selector=site_selector)

        patched = []

        for widget in self.widgets:
            kind = widget.attrs.get("widget")

            if kind is None:
                patched.append(
                    UnfoldAdminSelectWidget(
                        attrs=deepcopy(widget.attrs),
                        choices=widget.choices,
                    ),
                )
            elif kind == "external_link":
                patched.append(
                    UnfoldAdminURLInputWidget(
                        attrs=deepcopy(widget.attrs),
                    ),
                )
            elif kind == "internal_link":
                patched.append(
                    UnfoldLinkAutoCompleteWidget(
                        attrs=deepcopy(widget.attrs),
                    ),
                )
            elif kind == "anchor":
                patched.append(
                    UnfoldAdminTextInputWidget(
                        attrs=deepcopy(widget.attrs),
                    ),
                )
            else:
                patched.append(widget)

        self.widgets = patched


class UnfoldLinkFormField(LinkFormField):
    widget = UnfoldLinkWidget
