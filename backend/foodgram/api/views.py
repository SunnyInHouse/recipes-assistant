import io

from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.colors import navy, olive
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from recipes.models import (FavoriteList, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingList, Tag)
from users.models import Subscribe, User

from . import services
from .filters import RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (FavoriteSerializer, GetTokenSerializer,
                          IngredientSerielizer, ListSubscriptionsSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          SubscribeSerializer, TagSerielizer,
                          UserChangePasswordSerializer, UserSerializer)


class UserViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin,
                  GenericViewSet):
    """
    Вьюсет для работы с пользователями.
    URL - /users/.
    """

    name = 'Обработка запросов о пользователях'
    description = 'Обработка запросов о пользователях'

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'set_password':
            return UserChangePasswordSerializer
        if self.action == 'subscriptions':
            return ListSubscriptionsSerializer
        if self.action in ('subscribe'):
            return SubscribeSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ('list', 'create'):
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    @action(
        methods=['POST', ],
        url_path='set_password',
        detail=False
    )
    def set_password(self, request):
        """
        Метод для обработки запроса POST на изменение пароля авторизованным
        пользователем.
        URL - /users/set_password/.
        """

        user = request.user
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['GET', ],
        url_path='me',
        detail=False
    )
    def me(self, request):
        """
        Метод для обработки запроса GET на получение данных профиля текущего
        пользователя.
        URL - /users/me/.
        """

        user = request.user
        serializer = self.get_serializer(user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        methods=['GET', ],
        url_path='subscriptions',
        detail=False
    )
    def subscriptions(self, request):
        """
        Метод для обработки GET запросов на получение списка пользователей, на
        которых подписан текущий пользователь. В выдачу добавляются рецепты.
        URL - /users/subscriptions/.
        """

        user = request.user
        queryset = User.objects.filter(authors__user_subscriber=user)

        page = self.paginate_queryset(queryset)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        methods=['POST', 'DELETE'],
        url_path='(?P<id>[^/.]+)/subscribe',
        detail=False,
    )
    def subscribe(self, request, id):
        """
        Метод для обработки POST и DELETE запросов на создание/удаление
        подписки на пользователя (его данные указаны в path параметре id).
        URL = /users/{id}/subscribe/.
        """

        return services.add_del_smth_to_somewhere(
            request, id, self.get_serializer, User, Subscribe
        )


class GetTokenView(ObtainAuthToken):
    """
    Класс для обработки POST запросов для получения токена авторизации по email
    и паролю.
    URL - /auth/token/login/.
    """

    name = 'Получение токена'
    description = 'Получение токена'
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Функция для обработки POST запроса, создает токен аутентификации при
        предоставлении корректных email и пароля.
        """
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    'auth_token': token.key
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class DelTokenView(APIView):
    """
    Класс для обработки POST запросов для удаления токена авторизации текущего
    пользователя.
    URL - /auth/token/logout/.
    """

    name = 'Удаление токена'
    description = 'Удаление токена'
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Функция для обработки POST запроса, удаляет токен аутентификации.
        """
        token = request.auth
        token.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewset(ReadOnlyModelViewSet):
    """
    Вьюсет для получения списка тегов и отдельного тега.
    URL = /tags/.
    """

    name = 'Обработка запросов о тегах'
    description = 'Обработка запросов о тегах'

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

    name = 'Обработка запросов об ингридиентах'
    description = 'Обработка запросов об ингридиентах'

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

    name = 'Обработка запросов о рецептах'
    description = 'Обработка запросов о рецептах'

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = (AllowAny,)
        elif self.action in ('update', 'destroy', 'partial_update'):
            permission_classes = (IsOwnerOrReadOnly,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.action == 'shopping_cart':
            return ShoppingListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        url_path='(?P<id>[^/.]+)/favorite',
        detail=False,
    )
    def favorite(self, request, id):
        """
        Метод для обработки POST и DELETE запросов на добавление/удаление
        рецепта в избранное пользователя по id рецепта.
        URL = recipes/{id}/favorite/.
        """

        return services.add_del_smth_to_somewhere(
            request, id, self.get_serializer, Recipe, FavoriteList
        )

    @action(
        methods=['POST', 'DELETE'],
        url_path='(?P<id>[^/.]+)/shopping_cart',
        detail=False,
    )
    def shopping_cart(self, request, id):
        """
        Метод для обработки POST и DELETE запросов на добавление/удаление
        рецепта в список покупок пользователя по id рецепта.
        URL = recipes/{id}/shopping_cart/.
        """

        return services.add_del_smth_to_somewhere(
            request, id, self.get_serializer, Recipe, ShoppingList
        )

    @action(
        methods=['GET', ],
        url_path='download_shopping_cart',
        detail=False,
    )
    def download_shopping_cart(self, request):
        """
        Метод для загрузки списка покупок в формате PDF при помощи ReportLab.
        URL = recipes/download_shopping_cart/.
        """

        user = request.user
        ingredient_list_user = (
            IngredientInRecipe.objects.
            prefetch_related('ingredient', 'recipe').
            filter(recipe__shoppings__user=user).
            values_list('ingredient__name', 'ingredient__measurement_unit')
        )

        shopping_list = ingredient_list_user.annotate(amount=Sum('quantity'))

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('Arial', 'Arial Unicode.ttf'))

        p.setFont('Arial', 20)
        y = 810
        p.setFillColor(olive)
        p.drawString(55, y, 'Список покупок')
        y -= 30

        p.setFont('Arial', 14)
        p.setFillColor(navy)
        string_number = 1
        for i in shopping_list:
            p.drawString(
                15, y,
                f'{string_number}. {i[0].capitalize()} ({i[1]}) - {i[2]}'
            )
            y -= 20
            string_number += 1

        p.showPage()
        p.save()
        buffer.seek(0)

        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_list.pdf',
            status=status.HTTP_200_OK
        )
