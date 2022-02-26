from rest_framework import serializers

from .models import (FavoriteList, Ingredient, IngredientInRecipe, Recipe, Tag,
    ShoppingList)

from users.serializers import UserSerializer

from .services import check_is_it_in

from .fields import Base64ImageField


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


class RecipeListGetSerializer(serializers.ModelSerializer):
    """
    Сериалиализатор для обработки GET запросов о рецептах.
    """

    author = UserSerializer(read_only=True)
    tags = TagSerielizer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_recipe',
        read_only=True
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


class RecipeCreateUpdateDelSerializer(serializers.ModelSerializer):
    """
    Сериалиализатор для обработки POST, UPDATE, DELETE запросов на создание рецепта.
    """

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientInRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        return data

    def create(self, validated_data):
        """
        Функция для создания рецепта со списком ингридиентов и тегами.
        """
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                ingredient_id = ingredient['ingredient']['id'],
                quantity = ingredient['quantity'],
                recipe=recipe
            )
                for ingredient in ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        """
        Функция для обновления существующего рецепта.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = (
            validated_data.get('cooking_time', instance.cooking_time)
        )
        instance.tags.set(validated_data.get('tags', instance.tags))
        instance.ingredients = ...
  
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Функция для вывода данных сериализатором.
        """
        return RecipeListGetSerializer(instance, context={
                'request': self.context.get('request'),
            }).data

