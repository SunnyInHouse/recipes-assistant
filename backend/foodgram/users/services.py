from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from rest_framework import serializers


def password_verification(value):
    """
    Функция для проверки корректности введенного пользователем пароля.
    """
    help_text = password_validators_help_texts()
    if validate_password(value):
            return value
    raise serializers.ValidationError('Указан некорректный новый пароль. К '
            'паролю предъявляются следующие требования: '
            f'{help_text}')