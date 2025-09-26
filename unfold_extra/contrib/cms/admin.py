from typing import Optional, Any
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


from .forms import (
    AddPageForm,
    AdvancedSettingsForm,
    ChangePageForm,
    DuplicatePageForm,
    PageUserGroupForm,
)

from django.http import HttpResponse
from cms.admin.pageadmin import MODAL_HTML_REDIRECT  # existing constant in django CMS
from cms.toolbar.utils import get_object_edit_url
from django.urls import reverse
from cms.utils.i18n import get_site_language_from_request
from cms.utils.conf import get_cms_setting
from cms.admin.pageadmin import get_site

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
class PageContentAdmin(ModelAdmin, BasePageContentAdmin):
    change_form_template = "admin/cms/page/change_form.html"
    add_form_template = "admin/cms/page/change_form.html"
    change_list_template = "unfold_extra/cms/page/tree/base.html"

    form = AddPageForm
    add_form = AddPageForm
    change_form = ChangePageForm
    duplicate_form = DuplicatePageForm
    # move_form = MovePageForm
    # changelist_form = ChangeListForm
    compressed_fields = True

    def response_change(self, request, obj):
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        url = get_object_edit_url(obj)
        return HttpResponse(MODAL_HTML_REDIRECT.format(url=url))


    def response_add(self, request, obj, post_url_continue=None):
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        url = get_object_edit_url(obj)
        return HttpResponse(MODAL_HTML_REDIRECT.format(url=url))


@admin.register(Page)
class PageAdmin(ModelAdmin, BasePageAdmin):
    change_form_template = "admin/cms/page/change_form.html"
    form = AdvancedSettingsForm
    compressed_fields = True
    inlines = UNFOLD_PERMISSION_ADMIN_INLINES

    @staticmethod
    def _language_from_request(request) -> str:
        site = get_site(request)
        lang = request.GET.get("language") or get_site_language_from_request(request, site_id=site.pk)
        return lang or get_cms_setting("LANGUAGE_CODE")

    def _edit_redirect_url(self, request, page) -> str:
        language = self._language_from_request(request)
        content: Optional[Any] = getattr(page, "get_admin_content", None)
        if callable(content):
            page_content = page.get_admin_content(language)
            if page_content:
                try:
                    return get_object_edit_url(page_content)
                except AttributeError:
                    pass
        return reverse(f"admin:{self.opts.app_label}_{self.opts.model_name}_change", args=[page.pk])

    # modal-close on save
    def response_change(self, request, obj) -> HttpResponse:
        if "_continue" in request.POST:
            return super().response_change(request, obj)
        url = self._edit_redirect_url(request, obj)
        return HttpResponse(MODAL_HTML_REDIRECT.format(url=url))

    def response_add(self, request, obj, post_url_continue=None) -> HttpResponse:
        if "_continue" in request.POST:
            return super().response_add(request, obj, post_url_continue)
        url = self._edit_redirect_url(request, obj)
        return HttpResponse(MODAL_HTML_REDIRECT.format(url=url))