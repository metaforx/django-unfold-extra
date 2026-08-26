"""Unfold widgets for the stock filer forms the admin renders by hand.

Copy, move, rename and resize each render a plain ``forms.Form`` from
``filer.admin.forms`` on their confirmation page, and "New Folder" renders
``filer.admin.views.NewFolderForm``. Unfold styles form fields through
``ModelAdmin.formfield_overrides``, which never reaches a form built (or
rendered) outside a ``ModelAdmin`` like these — so without this the widgets keep
Django's default markup and the pages look unstyled next to the admin's own
action confirmations.
"""

from filer.admin.forms import (
    CopyFilesAndFoldersForm,
    RenameFilesForm,
    ResizeImagesForm,
)
from filer.admin.views import NewFolderForm
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
    NewFolderForm: {"name": UnfoldAdminTextInputWidget},
}


def patch_filer_forms():
    """Swap in Unfold's widgets on filer's hand-rolled forms.

    ``base_fields`` is deep-copied per form instance, so patching the class
    attribute up front covers every later render.
    """
    for form, widgets in FORM_WIDGETS.items():
        for name, widget in widgets.items():
            field = form.base_fields[name]
            # Carry over what the field put on its widget (``maxlength`` and
            # friends), minus the stock admin classes Unfold replaces.
            attrs = {k: v for k, v in field.widget.attrs.items() if k != "class"}
            field.widget = widget(attrs=attrs)
            # A fresh widget starts without the field's choices (ModelChoiceField
            # only hands them over in its own __init__).
            if hasattr(field, "choices"):
                field.widget.choices = field.choices
