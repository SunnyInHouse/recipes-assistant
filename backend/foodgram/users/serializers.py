from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password, password_changed, password_validators_help_texts
from django.contrib.auth.hashers import check_password

from users.models import Subscribe, User
from . services import password_verification


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обработки GET запросов о пользователях для /users
    и /users/me.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name','last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Функция получает информацию о подписке на пользователя у автора
        запроса.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscribers.filter(user_author=obj).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обработки запросов POST на создание пользователей на
    /users.
    """

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
    
    def validate_password(self, value):
        password_verification(value)


class UserChangePasswordSerializer(serializers.Serializer):
    """
    Сериализатор для обработки запросов POST на смену пароля на
    /users/set_password.
    """

    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)

    def update(self, instance, validated_data):
        instance.password = instance.set_password(validated_data['new_password'])
        password_changed(validated_data['new_password'], user=instance)
        instance.save()
        return instance
    
    def validate_current_password(self, value):
        """
        Метод проверяет, что указанный пароль соответствует паролю
        пользователя, отправившему запрос.
        """
        if check_password(value, self.instance.password):
            return value
        raise serializers.ValidationError('Указан неверный текущий пароль пользователя.')

    def validate_new_password(self, value):
        """
        Метод проверяет, что новый пароль соответствует настройкам безопасности.
        """
        password_verification(value)
