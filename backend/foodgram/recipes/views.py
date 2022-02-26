
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework import status
from rest_framework.response import Response

from .models import Ingredient, Recipe, Tag
from .serializers import (IngredientSerielizer, RecipeListGetSerializer,
                        RecipeCreateUpdateDelSerializer, 
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
    Вьюсет для получения списка ингридиентов и отдельного ингридиента.
    Возможен поиск ингридиентов по имени (параметр name в строке запроса).
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
    # serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'destroy', 'partial_update'):
            return RecipeCreateUpdateDelSerializer
        if self.action in ('list', 'retrieve'):
            return RecipeListGetSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



#  задача view - данные собрать, сдоеать запросы и тп (отвечает за получение даннх любым способом)
# задача сериализатора - эти данные правильно сохранить, работать с подготовленными данными


# максимально валидация в модели 