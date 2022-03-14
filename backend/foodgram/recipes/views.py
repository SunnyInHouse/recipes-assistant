from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework import status
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Ingredient, Recipe, Tag
from .serializers import (IngredientSerielizer, RecipeSerializer, 
                        TagSerielizer)


class TagViewset(ReadOnlyModelViewSet):
    """
    Вьюсет для получения списка тегов и отдельного тега.
    URL = /tags/.
    """

    permission_classes = (AllowAny,)
    serializer_class = TagSerielizer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewset(ReadOnlyModelViewSet):
    """
    Вьюсет для получения списка ингредиентов и отдельного ингредиента.
    Возможен поиск ингредиентов по имени (параметр name в строке запроса).
    URL = /tags/.
    """

    permission_classes = (AllowAny,)
    serializer_class = IngredientSerielizer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (SearchFilter, )
    search_fields = ('name', )


class RecipeViewset(ModelViewSet):
    """
    Вьюсет для работы с запросами о рецептах - просмотр списка рецептов,
    просмотр отдельного рецепта, создание, изменение и удаление рецепта.
    URL - /recipes/.
    """

    permission_classes = (AllowAny,)
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
#  написать фильтры, пермишн

# добавить функции для favourite shopping_list

#  задача view - данные собрать, сдоеать запросы и тп (отвечает за получение даннх любым способом)
# задача сериализатора - эти данные правильно сохранить, работать с подготовленными данными


# максимально валидация в модели 