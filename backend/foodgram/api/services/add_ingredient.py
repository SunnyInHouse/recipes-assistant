"""
Добавляет ингредиенты из словаря ingredients в рецепт recipe.
"""

from recipes.models import (IngredientInRecipe, Recipe)


def add_ingredients_to_recipe(recipe: Recipe, ingredients: dict) -> None:
    
    IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    ingredient_id=ingredient['ingredient']['id'],
                    quantity=ingredient['quantity'],
                    recipe=recipe
                )
                for ingredient in ingredients
            ]
        )
