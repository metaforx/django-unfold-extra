from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin

admin.site.unregister(User)

@admin.register(User)
class PageUserGroupAdmin(UserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    pass