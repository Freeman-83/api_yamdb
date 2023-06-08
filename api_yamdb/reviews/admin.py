from django.contrib import admin

from .models import (Category,
                     Genre,
                     Title,
                     TitleGenre,
                     CustomUser)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'confirmation_code', 'first_name',
                    'last_name', 'role', 'bio', 'password',)
    search_fields = ('username',)
    list_filter = ('username',)
    list_editable = ('role',)
    empty_value_display = '-пусто-'


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
