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


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions'
            ),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

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
