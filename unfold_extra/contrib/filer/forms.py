"""Unfold widgets for the forms behind filer's changelist actions.

Copy, move, rename and resize each render a plain ``forms.Form`` from
``filer.admin.forms`` on their confirmation page. Unfold styles form fields
through ``ModelAdmin.formfield_overrides``, which never reaches a form built by
hand like these — so without this the widgets keep Django's default markup and
the pages look unstyled next to the admin's own action confirmations.
"""

from filer.admin.forms import (
    CopyFilesAndFoldersForm,
    RenameFilesForm,
    ResizeImagesForm,
)
from unfold.widgets import (
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget,
    UnfoldBooleanWidget,
)

FORM_WIDGETS = {
    CopyFilesAndFoldersForm: {"suffix": UnfoldAdminTextInputWidget},
    RenameFilesForm: {"rename_format": UnfoldAdminTextInputWidget},
    ResizeImagesForm: {
        "thumbnail_option": UnfoldAdminSelectWidget,
        "width": UnfoldAdminIntegerFieldWidget,
        "height": UnfoldAdminIntegerFieldWidget,
        "crop": UnfoldBooleanWidget,
        "upscale": UnfoldBooleanWidget,
    },
}


def patch_filer_action_forms():
    """Swap in Unfold's widgets on filer's action forms.

    ``base_fields`` is deep-copied per form instance, so patching the class
    attribute up front covers every later render.
    """
    for form, widgets in FORM_WIDGETS.items():
        for name, widget in widgets.items():
            field = form.base_fields[name]
            field.widget = widget()
            # A fresh widget starts without the field's choices (ModelChoiceField
            # only hands them over in its own __init__).
            if hasattr(field, "choices"):
                field.widget.choices = field.choices
