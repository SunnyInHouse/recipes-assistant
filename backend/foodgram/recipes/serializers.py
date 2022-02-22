from rest_framework import serializers

from .models import (FavoriteList, Ingredient, IngredientInRecipe, Recipe, Tag,
    TagRecipe, ShoppingList)

from users.serializers import UserSerializer

from .services import check_is_it_in

class TagSerielizer(serializers.ModelSerializer):
    """
    Сериализатор для получения списка тегов и отдельного тега.
    """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerielizer(serializers.ModelSerializer):
    """
    Сериализатор для получения списка ингридиентов и отдельного ингридиента.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения списка ингридиентов в рецепте с указанием
    количества.
    """

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField(source='quantity')

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериалиализатор для обработки запросов о рецептах.
    """

    author = UserSerializer(read_only=True)
    tags = TagSerielizer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """
        Функция проверяет, добавлен ли рецепт в избранное.
        """
        return check_is_it_in(self, obj, FavoriteList)

    def get_is_in_shopping_cart(self, obj):
        """
        Функция проверяет, добавлен ли рецепт в список покупок.
        """
        return check_is_it_in(self, obj, ShoppingList)

    def create(self, validated_data):
        """
        Создание рецепта.
        """
        tags = validated_data.pop('tags')
        print(tags)
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag, status = Tag.objects.get(**tag)
            TagRecipe.objects.create(
                tag = current_tag,
                recipe = recipe
            )
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(ingredient['id'])
            IngredientInRecipe.objects.create(
                ingredient = current_ingredient,
                recipe = recipe,
                quantity = ingredient['amount']
            )
        return recipe
