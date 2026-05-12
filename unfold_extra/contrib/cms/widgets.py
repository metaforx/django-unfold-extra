from cms.forms.utils import get_page_choices, get_site_choices
from cms.forms.widgets import PageSelectWidget
from unfold.widgets import UnfoldAdminSelectWidget


class UnfoldPageSelectWidget(PageSelectWidget):
    """PageSelectWidget with Unfold-styled selects in a stacked layout."""

    template_name = "unfold_extra/cms/widgets/pageselectwidget.html"

    def _build_widgets(self):
        site_choices = get_site_choices()
        page_choices = get_page_choices()
        self.site_choices = site_choices
        self.choices = page_choices
        self.widgets = (
            UnfoldAdminSelectWidget(choices=site_choices),
            UnfoldAdminSelectWidget(choices=[("", "----")]),
            UnfoldAdminSelectWidget(choices=self.choices),
        )


class UnfoldPageSelectInlineWidget(UnfoldPageSelectWidget):
    """Inline-safe variant: patches the ``__prefix__`` bug in cloned rows."""

    class Media:
        js = ("unfold_extra/cms/js/pageselect_inline.js",)
