"""
Добавляет и удаляет объект типа model_smth в/из список/ка model_somewhere
по его id. Используется для добавления/удаления рецептов в избранное/список
покупок и для добавления/удаления авторов в подписки.
"""

from decimal import Decimal

from django.db.models import Model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

# from recipes.models import (
#                             ShoppingList) #FavoriteList,
from users.models import Subscribe


def add_del_smth_to_somewhere(
    request: Request, id: Decimal, serializer: ModelSerializer,
    model_smth: Model, model_somewhere: Model
) -> Response:

    smth = get_object_or_404(model_smth, id=int(id))

    if request.method == 'POST':

        if model_somewhere is Subscribe:
            data = {
                'user_subscriber': request.user.id,
                'user_author': id,
            }
        else:
            data = {
                'user': request.user.id,
                'recipes': id,
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