# from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import password_changed
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from users.models import Subscribe, User

from .services import password_verification


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


class UserChangePasswordSerializer(serializers.Serializer):
    """
    Сериализатор для обработки запросов POST на смену пароля.
    """

    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128, min_length=8)

    def update(self, instance, validated_data):
        instance.password = (
            instance.set_password(validated_data['new_password'])
        )
        password_changed(validated_data['new_password'], user=instance)
        instance.save()
        return instance

    def validate_current_password(self, value):
        """
        Метод проверяет, что указанный пароль соответствует паролю
        пользователя, отправившему запрос.
        """
        if value == self.instance.password:
            return value
        raise serializers.ValidationError(
            'Указан неверный текущий пароль пользователя.'
        )

    def validate_new_password(self, value):
        password_verification(value)


class GetTokenSerializer(serializers.Serializer):
    """
    Сериализатор для обработки запросов на получение токена.
    """

    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128)

    def validate(self, data):
        """
        Проверяет, что предоставленный пользователем email соотвествует
        пользователю в базе данных и указанный пароль корректен для
        пользователя с указанным e-mail.
        """
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Предоставлен email незарегистрированного пользователя.'
            )

        if user.password==data['password']: #user.check_password(data['password']):
            return data
        raise serializers.ValidationError(
            'Неверный пароль для пользователя с указанным email.'
        )


class RecipesForListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения данных о рецептах для выдачи их в списке
    подписок.
    """

    class Meta:
        model = User
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
        return RecipesForListSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """
        Функция считает число рецептов у пользователя, на которого подписан
        автор запроса.
        """
        return obj.recipes.count()
