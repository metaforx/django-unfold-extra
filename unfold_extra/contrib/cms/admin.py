from django.contrib import admin

from cms.admin.pageadmin import PageAdmin as BasePageAdmin
from cms.admin.pageadmin import PageContentAdmin as BasePageContentAdmin
from cms.admin.permissionadmin import (
    GlobalPagePermissionAdmin as BaseGlobalPagePermissionAdmin,
    ViewRestrictionInlineAdmin,
    PagePermissionInlineAdmin,
)
from cms.admin.useradmin import (
    PageUserAdmin,
    PageUserGroupAdmin as BasePageUserGroupAdmin,
)
from cms.models import GlobalPagePermission, Page, PageContent, PageUser, PageUserGroup
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from cms.utils.conf import get_cms_setting

from .forms import (
    AddPageForm,
    AdvancedSettingsForm,
    ChangePageForm,
    DuplicatePageForm,
    PageUserGroupForm,
)

admin.site.unregister(PageUserGroup)
admin.site.unregister(GlobalPagePermission)
admin.site.unregister(Page)
admin.site.unregister(PageContent)
admin.site.unregister(PageUser)

@admin.register(PageUserGroup)
class PageUserGroupAdmin(BasePageUserGroupAdmin, ModelAdmin):
    form = PageUserGroupForm
    compressed_fields = True

@admin.register(PageUser)
class PageUserGroupAdmin(PageUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    pass


@admin.register(GlobalPagePermission)
class GlobalPagePermissionAdmin(BaseGlobalPagePermissionAdmin, ModelAdmin):
    compressed_fields = True

class UnfoldViewRestrictionInlineAdmin(ViewRestrictionInlineAdmin, TabularInline):
    tab = True
    autocomplete_fields = ["user", "group"]

class UnfoldVPagePermissionInlineAdmin(PagePermissionInlineAdmin, TabularInline):
    tab = True


UNFOLD_PERMISSION_ADMIN_INLINES = []
if get_cms_setting('PERMISSION'):
    admin.site.unregister(GlobalPagePermission)
    admin.site.register(GlobalPagePermission, GlobalPagePermissionAdmin)
    UNFOLD_PERMISSION_ADMIN_INLINES.extend([
        UnfoldViewRestrictionInlineAdmin,
        UnfoldVPagePermissionInlineAdmin,
    ])


@admin.register(PageContent)
class PageContentAdmin(BasePageContentAdmin, ModelAdmin):
    form = AddPageForm
    add_form = AddPageForm
    change_form = ChangePageForm
    duplicate_form = DuplicatePageForm

    # move_form = MovePageForm
    # changelist_form = ChangeListForm

    compressed_fields = True

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.change_list_template = "unfold_extra/cms/page/tree/base.html"
        self.change_form_template = "unfold_extra/cms/page/change_form.html"


@admin.register(Page)
class PageAdmin(BasePageAdmin, ModelAdmin):
    form = AdvancedSettingsForm

    compressed_fields = True
    inlines = UNFOLD_PERMISSION_ADMIN_INLINES

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.change_form_template = "unfold_extra/cms/page/change_form.html"
