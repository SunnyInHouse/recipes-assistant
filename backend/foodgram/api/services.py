"""
Вспомогательные функции для приложения.
"""

import io
from decimal import Decimal
from typing import TextIO, Union

from django.contrib.auth.password_validation import (
    password_validators_help_texts, validate_password)
from django.db.models import Model
from django.shortcuts import get_object_or_404
from reportlab.lib.colors import navy, olive
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ValidationError

from recipes.models import (FavoriteList, IngredientInRecipe, Recipe,
                            ShoppingList)
from users.models import Subscribe


def password_verification(value: str) -> Union[str, ValidationError]:
    """
    Функция для проверки корректности полученного от пользователя пароля.
    """

    help_text = password_validators_help_texts()

    if validate_password(value) is None:
        return value

    raise ValidationError(
        'Указан некорректный новый пароль. К паролю предъявляются следующие'
        f'требования: {help_text}'
    )


def check_is_it_in(
        serializer_data: dict, obj_it: Recipe, obj_in: Model
) -> bool:
    """
    Проверяет, что объект из запроса (obj_it) находится в списке объектов
    типа obj_in пользователя - автора запроса.
    """

    user = serializer_data.context['request'].user

    if user.is_authenticated:
        return obj_in.objects.filter(user=user, recipes=obj_it).exists()

    return False


def add_ingredients_to_recipe(recipe: Recipe, ingredients: dict) -> None:
    """
    Добавляет ингредиенты из словаря ingredients в рецепт recipe.
    """
    IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    ingredient_id=ingredient['ingredient']['id'],
                    quantity=ingredient['quantity'],
                    recipe=recipe
                )
                for ingredient in ingredients
            ]
        )


def check_value_is_0_or_1(value: Decimal) -> bool:
    """
    Проверяет, что значение value равно либо 0, либо 1.
    """

    if value in (0, 1):
        return True

    return False


def add_del_smth_to_somewhere(
    request: Request, id: Decimal, serializer: ModelSerializer,
    model_smth: Model, model_somewhere: Model
) -> Response:
    """
    Добавляет и удаляет объект типа model_smth в/из список/ка model_somewhere
    по его id. Используется для добавления/удаления рецептов в избранное/список
    покупок и для добавления/удаления авторов в подписки.
    """

    smth = get_object_or_404(model_smth, id=int(id))

    if request.method == 'POST':

        if model_somewhere is Subscribe:
            model_field_1 = 'user_subscriber'
            model_field_2 = 'user_author'

        model_field_1 = 'user'
        model_field_2 = 'recipes'

        data = {
            model_field_1: request.user.id,
            model_field_2: id,
        }

        serializer = serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    # удаление
    try:
        if model_somewhere is Subscribe:
            smth_in_somewhere = model_somewhere.objects.get(
                user_subscriber=request.user,
                user_author=smth,
            )
            error_text = 'Указанной подписки не существует.'

        if model_somewhere is FavoriteList:
            error_text = 'Указанный рецепт не добавлен в избранное.'

        if model_somewhere is ShoppingList:
            error_text = 'Указанный рецепт не добавлен в список покупок.'

        smth_in_somewhere = model_somewhere.objects.get(
                user=request.user,
                recipes=smth,
        )

    except model_somewhere.DoesNotExist:
        return Response(
            {'errors': f'{error_text}', },
            status=status.HTTP_400_BAD_REQUEST
        )

    smth_in_somewhere.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


def create_pdf(data: list, title: str) -> TextIO:
    """
    Создает pdf-файл при помощи ReportLab.
    """

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont('Arial', 'Arial Unicode.ttf'))

    p.setFont('Arial', 20)
    y = 810
    p.setFillColor(olive)
    p.drawString(55, y, f'{title}')
    y -= 30

    p.setFont('Arial', 14)
    p.setFillColor(navy)
    string_number = 1
    for i in data:
        p.drawString(
            15, y,
            f'{string_number}. {i[0].capitalize()} ({i[1]}) - {i[2]}'
        )
        y -= 20
        string_number += 1

    p.showPage()
    p.save()
    buffer.seek(0)

    return buffer
