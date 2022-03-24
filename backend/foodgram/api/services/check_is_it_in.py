"""
Проверяет, что объект из запроса (obj_it) находится в списке объектов
типа obj_in пользователя - автора запроса.
"""

from django.db.models import Model

from recipes.models import Recipe
from users.models import User


def check_is_it_in(
        user_author: User, obj_it: Recipe, obj_in: Model
) -> bool:

    if user_author.is_authenticated:
        return obj_in.objects.filter(user=user_author, recipes=obj_it).exists()

    return False
