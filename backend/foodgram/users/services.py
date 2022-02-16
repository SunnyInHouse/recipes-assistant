from django.contrib.auth.password_validation import (
    password_validators_help_texts, validate_password)
from rest_framework import serializers


def password_verification(value):
    """
    Функция для проверки корректности полученного от пользователя пароля.
    """
    help_text = password_validators_help_texts()
    if validate_password(value) is None:
        return value
    raise serializers.ValidationError(
        'Указан некорректный новый пароль. К паролю предъявляются следующие'
        f'требования: {help_text}'
    )
