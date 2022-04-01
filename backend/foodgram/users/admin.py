from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin

from .models import User, Subscribe
from recipes.models import Recipe


# class RecipeInline(admin.TabularInline):
#     model = Recipe
#     fields = ('name', 'text',)
#### дописать отобрадения полей со списками рецептов в избранном и в шоппинг листе

class CustomUserAdmin(UserAdmin):
    list_filter = (
        'email',
        'username',
    )
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
        # 'favorite_recipes',
        # 'shopping_recipes',
    )
    # inline = [
    #     RecipeInline,
    # ]


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'user_author',
    )
    search_fields = (
        'user_author',
        'user',
    )


class CustomUserInline(admin.TabularInline):
    model = User
    raw_id_fields = ['user']


class CustomTokenAdmin(TokenAdmin):
    inlines = [
        CustomUserInline,
    ]


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
