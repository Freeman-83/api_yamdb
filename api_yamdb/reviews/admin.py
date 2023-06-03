from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, ConfirmationCode


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username',)
    search_fields = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ConfirmationCode)
