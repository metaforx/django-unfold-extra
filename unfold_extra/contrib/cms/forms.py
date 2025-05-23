from cms.admin.forms import AddPageForm as BaseAddPageForm
from cms.admin.forms import AdvancedSettingsForm as BaseAdvancedSettingsForm
from cms.admin.forms import ChangePageForm as BaseChangePageForm
from cms.admin.forms import PageUserGroupForm as BasePageUserGroupForm
from unfold.widgets import (
    INPUT_CLASSES,
    SELECT_CLASSES,
    SWITCH_CLASSES,
    TEXTAREA_CLASSES,
)


class PageUserGroupForm(BasePageUserGroupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.fields:
            if key == "name":
                self.fields[key].widget.attrs["class"] = " ".join(
                    INPUT_CLASSES
                )
            else:
                self.fields[key].widget.attrs["class"] = " ".join(
                    SWITCH_CLASSES
                )


class AddPageForm(BaseAddPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in [
            "title",
            "slug",
            "menu_title",
            "page_title",
        ]:
            self.fields[key].widget.attrs["class"] = " ".join(INPUT_CLASSES)

        self.fields["meta_description"].widget.attrs["class"] = " ".join(
            TEXTAREA_CLASSES
        )


class ChangePageForm(BaseChangePageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in [
            "title",
            "slug",
            # "template",
            "page_title",
            "menu_title",
        ]:
            self.fields[key].widget.attrs["class"] = " ".join(INPUT_CLASSES)

        self.fields["meta_description"].widget.attrs["class"] = " ".join(
            TEXTAREA_CLASSES
        )

        # url options NOTE: django cms uses a input type 'text', we could use a UnfoldAdminURLInputWidget instead...
        self.fields["overwrite_url"].widget.attrs["class"] = " ".join(
            INPUT_CLASSES
        )
        self.fields["redirect"].widget.attrs["class"] = " ".join(
            SELECT_CLASSES
        )

        # menu options
        self.fields["soft_root"].widget.attrs["class"] = " ".join(
            SWITCH_CLASSES
        )
        self.fields["limit_visibility_in_menu"].widget.attrs["class"] = (
            " ".join(SELECT_CLASSES)
        )

        # headers
        self.fields["xframe_options"].widget.attrs["class"] = " ".join(
            SELECT_CLASSES
        )


class DuplicatePageForm(AddPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["source"].widget.attrs["class"] = " ".join(SELECT_CLASSES)


class AdvancedSettingsForm(BaseAdvancedSettingsForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["navigation_extenders"].widget.attrs["class"] = " ".join(
            SELECT_CLASSES
        )

        self.fields["application_configs"].widget.attrs["class"] = " ".join(
            SELECT_CLASSES
        )

        self.fields["application_urls"].widget.attrs["class"] = " ".join(
            SELECT_CLASSES
        )
