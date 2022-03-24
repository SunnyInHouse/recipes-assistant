"""
Проверки соответствия настройкам паролей полученного от пользователя пароля.
"""

from django.contrib.auth.password_validation import (
    password_validators_help_texts, validate_password)
from rest_framework.serializers import ValidationError


def password_verification(value: str) -> str:

    help_text = password_validators_help_texts()

    if validate_password(value) is None:
        return value

    raise ValidationError(
        'Указан некорректный новый пароль. К паролю предъявляются следующие'
        f'требования: {help_text}'
    )