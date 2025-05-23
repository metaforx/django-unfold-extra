from cms.forms.utils import get_page_choices, get_site_choices
from cms.forms.widgets import PageSelectWidget
from unfold.widgets import UnfoldAdminSelectWidget


class UnfoldPageSelectWidget(PageSelectWidget):
    def _build_widgets(self):
        site_choices = get_site_choices()
        page_choices = get_page_choices()
        self.site_choices = site_choices
        self.choices = page_choices
        self.widgets = (
            UnfoldAdminSelectWidget(choices=site_choices),
            UnfoldAdminSelectWidget(choices=[("", "----")]),
            UnfoldAdminSelectWidget(
                choices=self.choices, attrs={"style": "display:none;"}
            ),
        )
