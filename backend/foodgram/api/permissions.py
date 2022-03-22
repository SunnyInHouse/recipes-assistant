"""
Описание кастомных классов разрешений.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешение уровня объекта на доступ к объекту только автору
    """
    message = 'Доступ разрешен только автору.'

    def has_permissions(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
