from xml.dom import ValidationErr
from rest_framework import serializers

from .models import (FavoriteList, Ingredient, IngredientInRecipe, Recipe, Tag,
    ShoppingList)

from users.serializers import UserSerializer

from . import services

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
    Сериализатор для получения списка ингредиентов и отдельного ингредиента.
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
    Сериализатор для получения списка ингредиентов в рецепте с указанием
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
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_recipe'
    )
    image = Base64ImageField()
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
        return services.check_is_it_in(self, obj, FavoriteList)

    def get_is_in_shopping_cart(self, obj):
        """
        Функция проверяет, добавлен ли рецепт в список покупок.
        """
        return services.check_is_it_in(self, obj, ShoppingList)

    def validate_tags(self, value):
        """
        Функция для валидации тегов.
        """
        if len(value)==0:
            raise serializers.ValidationError('Укажите теги рецепта.')
        for tag in value:
            if tag not in Tag.objects.all():
                raise serializers.ValidationError(
                    'Указанного тега не существует.'
                )
        return value

    def validate_ingredients(self, value):
        """
        Функция для валидации словаря ингредиентов. Проверяет, что в переданном
        словаре присутствуют ингредиенты, существующие в базе данных, и для
        них указано корректное количество (более 0). Также присутствует
        проверка попытки добавления повторяющихся элементов.
        """
        if len(value)==0:
            raise serializers.ValidationError(
                'Укажите ингредиенты для рецепта.'
            )
        set_ingr_id = set()
        for ingredient in value:
            ingredient_id = ingredient['ingredient']['id']   
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f"Ингредиента с id {ingredient_id} нет в базе данных."
                )
            if ingredient_id in set_ingr_id:
                raise serializers.ValidationError(
                    "В рецепте не может быть нескольких одинаковых "
                    "ингредиентов. Повторяющийся ингредиент - ингредиент с "
                    f"id {ingredient_id}."
                )
            set_ingr_id.add(ingredient_id)
            if ingredient['quantity'] <= 0:
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть более 0. Укажите "
                    f"корректное количество ингредиента с id {ingredient_id}."
                )
        return value

    def validate(self, data):
        """
        Функция для валидации входящих данных.
        """
        
        return data

    def create(self, validated_data):
        """
        Функция для создания рецепта со списком ингредиентов и тегами.
        """
        ingredients = validated_data.pop('ingredient_recipe')
        new_recipe = super().create(validated_data)
        services.add_ingredients_in_recipe(new_recipe, ingredients)
        return new_recipe

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
        instance.ingredients.clear()
        instance.save()

        services.add_ingredients_in_recipe(instance, validated_data['ingredient_recipe'])
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Функция для вывода данных сериализатором.
        """
        result = super().to_representation(instance)
        result['tags'] = TagSerielizer(instance.tags.all(), many=True).data
        return result
