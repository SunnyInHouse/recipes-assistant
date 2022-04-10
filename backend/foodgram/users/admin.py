from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from rest_framework.authtoken.admin import TokenAdmin

from .models import Subscribe, User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = UserCreationForm.Meta.model
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes


class FavoriteInline(admin.TabularInline):
    model = User.favorite_recipes.through
    extra = 1
    verbose_name = 'Избранный рецепт'
    verbose_name_plural = 'Избранные рецепты'


class ShoppingListInline(admin.StackedInline):
    model = User.shopping_recipes.through
    extra = 1
    verbose_name = 'Рецепт в списке покупок'
    verbose_name_plural = 'Список покупок'


class SubscribeInline(admin.StackedInline):
    model = User.subscribing.through
    fk_name = 'user'
    extra = 1
    verbose_name_plural = ' Список подписок'


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'user_permissions'
            ),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = (
        'date_joined',
        'last_login',
    )

    inlines = [
        FavoriteInline,
        ShoppingListInline,
        SubscribeInline,
    ]

    list_filter = (
        'email',
        'username',
    )
    list_display = (
        'username',
        'email',
    )


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
