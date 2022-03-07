"""
Вспомогательные функции и классы для приложения.
"""

from django.db.models import Model

from .models import Recipe, IngredientInRecipe


def check_is_it_in(
        serializer_data:dict, obj_it: Recipe, obj_in:Model
    ) -> bool:
    """
    Проверяет, что объект из запроса (obj_it) находится в списке объектов
    типа obj_in пользователя - автора запроса.
    """
    user = serializer_data.context['request'].user
    if user.is_authenticated:
        return obj_in.objects.filter(user=user, recipes=obj_it).exists()
    return False


def add_ingredients_in_recipe(recipe: Recipe, ingredients:dict) -> None:
    """
    Добавляет ингредиенты из словаря ingredients в рецепт recipe.
    """
    IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    ingredient_id = ingredient['ingredient']['id'],
                    quantity = ingredient['quantity'],
                    recipe=recipe
                )
                for ingredient in ingredients
            ]
        )
