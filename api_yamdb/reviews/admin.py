from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Category,
                     Genre,
                     Title,
                     TitleGenre,
                     CustomUser)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username',)
    search_fields = ('username',)


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'description', 'category')
    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = '-пусто-'


admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title, TitleAdmin)
admin.site.register(TitleGenre)
admin.site.register(CustomUser, CustomUserAdmin)
