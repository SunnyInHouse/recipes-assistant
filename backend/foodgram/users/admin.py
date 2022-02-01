from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


class CustomUserAdmin(UserAdmin):
    list_filter = (
        'email',
        'username',
    )


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'user_subscriber',
        'user_author',
    )
    search_fields = (
        'user_author',
        'user_subscriber',
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
