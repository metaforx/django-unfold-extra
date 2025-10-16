from cms.admin.forms import ChangeListForm, MovePageForm
from django.contrib import admin, messages

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

from django.http import HttpResponse, HttpResponseRedirect
from cms.admin.pageadmin import MODAL_HTML_REDIRECT  # existing constant in django CMS
from cms.toolbar.utils import get_object_edit_url
from django.urls import reverse
from cms.utils.conf import get_cms_setting

from .utils import (
    _admin_add_success_message,
    _admin_change_success_message,
    _admin_delete_success_message,
    _html_modal_redirect,
    _html_sidepanel_redirect,
    _language_from_request,
    _request_is_iframe,
    _request_is_toolbar_modal,
    _sidepanel_return_url,
)

admin.site.unregister(Page)
admin.site.unregister(PageContent)


if get_cms_setting('PERMISSION'):
    admin.site.unregister(PageUserGroup)
    admin.site.unregister(GlobalPagePermission)
    admin.site.unregister(PageUser)

    @admin.register(PageUserGroup)
    class PageUserGroupAdmin(BasePageUserGroupAdmin, ModelAdmin):
        form = PageUserGroupForm
        compressed_fields = True

    @admin.register(GlobalPagePermission)
    class GlobalPagePermissionAdmin(BaseGlobalPagePermissionAdmin, ModelAdmin):
        compressed_fields = True

    @admin.register(PageUser)
    class PageUserGroupAdmin(PageUserAdmin, ModelAdmin):
        form = UserChangeForm
        add_form = UserCreationForm
        change_password_form = AdminPasswordChangeForm
        pass


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
    move_form = MovePageForm
    changelist_form = ChangeListForm
    compressed_fields = True

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        """
        Disable the "save and add another" button in the admin interface.
        """
        context = dict(context or {})
        context["show_delete"] = False
        context["show_save_and_add_another"] = False
        return super().render_change_form(request, context, add, change, form_url, obj)


    def _changelist_url(self) -> str:
        """
        Generates the URL for the changelist view used to return to the admin after a successful operation.
        """
        return reverse(f"admin:{self.opts.app_label}_{self.opts.model_name}_changelist")

    def response_add(self, request, obj, post_url_continue=None) -> HttpResponse:
        """
        Handles special redirect behavior when an object is created, depending on the request.
        """
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        if _request_is_iframe(request):
            self.message_user(request,_admin_add_success_message(obj),messages.SUCCESS)
            if _request_is_toolbar_modal(request):
                return _html_modal_redirect(get_object_edit_url(obj))
            return _html_sidepanel_redirect(_sidepanel_return_url(request, self._changelist_url()))

        self.message_user(request,_admin_add_success_message(obj),messages.SUCCESS)
        return HttpResponseRedirect(_sidepanel_return_url(request, self._changelist_url()))

    def response_change(self, request, obj) -> HttpResponse:
        """
        Handles special redirect behavior when an object is changed, depending on the request.
        """
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        if _request_is_iframe(request):
            self.message_user(request,_admin_change_success_message(obj),messages.INFO)
            if _request_is_toolbar_modal(request):
                return _html_modal_redirect(get_object_edit_url(obj))
            return _html_sidepanel_redirect(_sidepanel_return_url(request, self._changelist_url()))

        self.message_user(request, _admin_change_success_message(obj), messages.INFO)
        return HttpResponseRedirect(_sidepanel_return_url(request, self._changelist_url()))


    def response_delete(self, request, obj_display, obj_id):
        """
        Handles the response after an object has been deleted.
        """
        changelist_url = self._changelist_url()

        if _request_is_iframe(request):
            self.message_user(request, _admin_delete_success_message(obj_display), messages.SUCCESS)
            return _html_sidepanel_redirect(_sidepanel_return_url(request, changelist_url))

        self.message_user(request, _admin_delete_success_message(obj_display), messages.SUCCESS)
        return HttpResponseRedirect(_sidepanel_return_url(request, changelist_url))

@admin.register(Page)
class PageAdmin(ModelAdmin, BasePageAdmin):
    change_form_template = "admin/cms/page/change_form.html"
    form = AdvancedSettingsForm
    compressed_fields = True
    inlines = UNFOLD_PERMISSION_ADMIN_INLINES


    @staticmethod
    def _changelist_url() -> str:
        return reverse(f"admin:cms_pagecontent_changelist")

    def _edit_redirect_url(self, request, page) -> str:
        """
        Constructs the redirect URL for editing a given page's advanced settings or returns the
        default admin change URL for the page.
        """
        language = _language_from_request(request)
        content = getattr(page, "get_admin_content", None)
        if callable(content):
            page_content = page.get_admin_content(language)
            if page_content:
                try:
                    return get_object_edit_url(page_content)
                except AttributeError:
                    pass
        return reverse(f"admin:{self.opts.app_label}_{self.opts.model_name}_change", args=[page.pk])


    def response_change(self, request, obj) -> HttpResponse:
        """
        Handles special redirect behavior when an object is changed, depending on the request.
        """
        if "_continue" in request.POST:
            return super().response_change(request, obj)


        if _request_is_iframe(request):
            self.message_user(request, _admin_change_success_message(obj), messages.INFO)
            if _request_is_toolbar_modal(request):
                url = self._edit_redirect_url(request, obj)
                return HttpResponse(MODAL_HTML_REDIRECT.format(url=url))
            return _html_sidepanel_redirect(self._changelist_url())

        self.message_user(request,_admin_change_success_message(obj),messages.INFO)
        return HttpResponseRedirect(_sidepanel_return_url(request, self._changelist_url()))


    # def response_add(self, request, obj, post_url_continue=None) -> HttpResponse:
    #     if "_continue" in request.POST:
    #         return super().response_add(request, obj, post_url_continue)
    #     url = self._edit_redirect_url(request, obj)
    #     return HttpResponse(MODAL_HTML_REDIRECT.format(url=url))