from django.contrib.admin.widgets import AutocompleteSelect
from django.forms import Select
from djangocms_attributes_field.widgets import AttributesWidget
from djangocms_link.fields import LinkWidget
from unfold.widgets import INPUT_CLASSES, SELECT_CLASSES


class UnfoldLinkWidget(LinkWidget):
    """djangocms-link's ``MultiWidget`` with Unfold classes on each sub-widget."""

    def __init__(self, site_selector=None):
        super().__init__(site_selector=site_selector)
        input_cls = " ".join(INPUT_CLASSES)
        select_cls = " ".join(SELECT_CLASSES)
        # Style each sub-widget by type, leaving the autocomplete sub-widget on
        # its select2 ``admin-autocomplete`` theme.
        for sub in self.widgets:
            if isinstance(sub, AutocompleteSelect):
                continue
            cls = select_cls if isinstance(sub, Select) else input_cls
            existing = sub.attrs.get("class", "")
            sub.attrs["class"] = f"{existing} {cls}".strip()


class UnfoldAttributesWidget(AttributesWidget):
    """``AttributesWidget`` styled via key/value attrs (it ignores ``self.attrs``)."""

    def __init__(self, *args, **kwargs):
        cls = " ".join(INPUT_CLASSES)
        kwargs.setdefault("key_attrs", {"class": cls})
        kwargs.setdefault("val_attrs", {"class": cls})
        super().__init__(*args, **kwargs)
