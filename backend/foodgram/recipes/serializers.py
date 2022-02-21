from rest_framework import serializers

from .models import Ingredient, Recipe, Tag, TagRecipe

from users.serializers import UserSerializer

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


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериалиализатор для обработки запросов о рецептах.
    """

    author = UserSerializer()
    tags = TagSerielizer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        """
        Создание рецепта.
        """
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag, status = Tag.objects.get_or_create(**tag)
            TagRecipe.objects.create(
                tag = current_tag,
                recipe = recipe
            )
        return recipe
