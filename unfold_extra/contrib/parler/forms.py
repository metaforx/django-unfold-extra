from parler.forms import TranslatableModelForm
from unfold.widgets import (
    UnfoldAdminFileFieldWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminURLInputWidget,
)

from unfold_extra.contrib.cms.widgets import UnfoldPageSelectWidget


class UnfoldTranslatableModelForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if self.fields[field].widget.__class__.__name__ == "TextInput":
                self.fields[field].widget = UnfoldAdminTextInputWidget()
            elif self.fields[field].widget.__class__.__name__ == "Textarea":
                self.fields[field].widget = UnfoldAdminTextareaWidget()
            elif self.fields[field].widget.__class__.__name__ == "URLInput":
                self.fields[field].widget = UnfoldAdminURLInputWidget()
            elif self.fields[field].widget.__class__.__name__ == "Select":
                self.fields[field].widget = UnfoldAdminSelectWidget()
            elif (
                self.fields[field].widget.__class__.__name__
                == "ClearableFileInput"
            ):
                self.fields[field].widget = UnfoldAdminFileFieldWidget()

            # CMS specific
            elif (
                self.fields[field].widget.__class__.__name__
                == "PageSelectWidget"
            ):
                self.fields[field].widget = UnfoldPageSelectWidget()
