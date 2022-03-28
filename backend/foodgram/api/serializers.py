from django.contrib.auth.password_validation import password_changed
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from recipes.models import (Ingredient, IngredientInRecipe,
                            Recipe,  Tag) #FavoriteList, ShoppingList,
from users.models import Subscribe, User

from . import services
from .fields import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обработки запросов о списке пользователей, отдельном
    пользователе и регистрации пользователя.
    """

    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с указанным username уже существует.'
            ),
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с указанным e-mail уже существует.'
            ),
        ]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed', )
        extra_kwargs = {
            'password': {'write_only': True}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=("username", "email"),
                message=(
                    "Задано не уникальное сочетание полей email " "и username."
                ),
            ),
        ]

    def get_is_subscribed(self, obj):
        """
        Функция получает информацию о подписке на пользователя у автора
        запроса.
        """

        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscribers.filter(user_author=obj).exists()
        return False

    def create(self, validated_data):
        """
        Функция для создания пользователя.
        """

        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def validate_password(self, value):
        """
        Функция проверяет заданный пользователем пароль на соответстие
        установленным требованиям к паролям.
        """

        return services.password_verification(value)


class UserChangePasswordSerializer(serializers.Serializer):
    """
    Сериализатор для обработки запросов POST на смену пароля.
    """

    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128, min_length=8)

    def update(self, instance, validated_data):
        """
        Функция для обновления пароля пользователя.
        """

        instance.set_password(validated_data['new_password'])
        password_changed(validated_data['new_password'], user=instance)
        instance.save()

        return instance

    def validate_current_password(self, value):
        """
        Функция проверяет, что указанный пароль соответствует паролю
        пользователя, отправившему запрос.
        """

        user = self.context.get('request').user

        if user.check_password(value):
            return value
        raise serializers.ValidationError(
            'Указан неверный текущий пароль пользователя.'
        )

    def validate_new_password(self, value):
        """
        Функция проверяет новый пароль на соответствие требованиям к паролям.
        """

        return services.password_verification(value)


class GetTokenSerializer(serializers.Serializer):
    """
    Сериализатор для обработки запросов на получение токена.
    """

    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128)

    def validate(self, data):
        """
        Функция проверяет, что предоставленный пользователем email соотвествует
        пользователю в базе данных и указанный пароль корректен для
        пользователя с указанным e-mail.
        """

        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Предоставлен email незарегистрированного пользователя.'
            )

        if user.check_password(data['password']):
            return data
        raise serializers.ValidationError(
            'Неверный пароль для пользователя с указанным email.'
        )


class RecipesMiniSerializers(serializers.ModelSerializer):
    """
    Сериализатор для получения данных о рецептах для выдачи их в списке
    подписок.
    """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class ListSubscriptionsSerializer(UserSerializer):
    """
    Сериализатор для обработки запросов на получение списка пользователей, на
    которых подписан текущий пользователь. В выдачу добавляются рецепты.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """
        Функция получает список рецептов пользователя. Отдает ограниченное
        автором запроса число рецептов (recipes_limit), если указано.
        """

        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]

        return RecipesMiniSerializers(recipes, many=True).data

    def get_recipes_count(self, obj):
        """
        Функция считает число рецептов у пользователя, на которого подписан
        автор запроса.
        """

        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обработки запросов на создание и удаление подписки на
    пользователя.
    """

    queryset = User.objects.all()
    user_author = serializers.PrimaryKeyRelatedField(queryset=queryset)
    user_subscriber = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscribe
        fields = ('user_subscriber', 'user_author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=("user_subscriber", "user_author"),
                message=(
                    "Вы уже подписаны на данного пользователя."
                ),
            ),
        ]

    def validate(self, data):
        """
        Функция проверяет, что пользователь не подписывается на самого себя.
        """

        id_user = data['user_subscriber']
        id_author = data['user_author']
        if id_user == id_author:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )

        return data

    def to_representation(self, instance):
        """
        Функция для получения представления объекта подписки в виде,
        запрошенном в ТЗ. (аналогично представлению в списке подписок)
        """

        data = instance.user_author

        return ListSubscriptionsSerializer(
            data,
            context={
                'request': self.context.get('request'),
            }
        ).data


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
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
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

        if self.context.get('request').user.is_authenticated:
            return obj.is_favorited
        return False


    def get_is_in_shopping_cart(self, obj):
        """
        Функция проверяет, добавлен ли рецепт в список покупок.
        """

        if self.context.get('request').user.is_authenticated:
            return obj.is_in_shopping_cart
        return False

    def validate_tags(self, value):
        """
        Функция для валидации тегов.
        """

        if len(value) == 0:
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

        if len(value) == 0:
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

    def create(self, validated_data):
        """
        Функция для создания рецепта со списком ингредиентов и тегами.
        """

        ingredients = validated_data.pop('ingredient_recipe')
        new_recipe = super().create(validated_data)
        services.add_ingredients_to_recipe(new_recipe, ingredients)

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

        services.add_ingredients_to_recipe(
            instance, validated_data['ingredient_recipe']
        )
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Функция для вывода данных сериализатором.
        """

        result = super().to_representation(instance)
        result['tags'] = TagSerielizer(instance.tags.all(), many=True).data

        return result


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    """
    Сериалиализатор для обработки запросов на добавление рецептов в избранное
    или в список покупок в зависимости от значения переданного в него параметра
    type_list.
    """

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    type_list = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'recipe',
            'user',
            'type_list',
        )

    def validate(self, data):
        """
        Функция для валидации входящих данных.
        """

        recipe = get_object_or_404(Recipe, id=data['recipe'].id)

        if data['type_list'] == 'favorite':
            error_text = 'список избранного'
            condition = User.objects.select_related('favorite_recipes').filter(
                username=data['user'].username,
                favorite_recipes=recipe
            ).exists()
        if data['type_list'] == 'shopping':
            error_text = 'список покупок'
            condition = User.objects.select_related('shopping_recipes').filter(
                username=data['user'].username,
                shopping_recipes=recipe
            ).exists()

        if condition:
            raise serializers.ValidationError(
                    f"Рецепт {recipe} уже добавлен в ваш {error_text}."
            )

        return data

    def create(self, validated_data):
        """
        Функция для добавление в список избранного/покупок рецепта.
        """

        user = validated_data['user']
        recipe = validated_data['recipe']

        if validated_data['type_list']=='favorite':
            user.favorite_recipes.add(recipe)
        if validated_data['type_list']=='shopping':
            user.shopping_recipes.add(recipe)

        return recipe

    def to_representation(self, instance):
        """
        Функция для вывода данных сериализатором.
        """

        return RecipesMiniSerializers(instance).data
