from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin

admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class PageUserGroupAdmin(UserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    pass

@admin.register(Group)
class PageUserGroupAdmin(GroupAdmin, ModelAdmin):
    pass