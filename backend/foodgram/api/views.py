from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
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

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Subscribe, User

from . import services
from .filters import RecipeFilter
from .mixins import CustomCreateDeleteMixin
from .pagination import CustomPageNumberPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (FavoriteShoppingSerializer, GetTokenSerializer,
                          IngredientSerielizer, ListSubscriptionsSerializer,
                          RecipeSerializer, SubscribeSerializer, TagSerielizer,
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
    lookup_field = 'id'
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.action in ('list', 'create'):
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'set_password':
            return UserChangePasswordSerializer
        if self.action == 'subscriptions':
            return ListSubscriptionsSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            subscriptions = user.subscribing.filter(id=OuterRef('id'))
            return User.objects.annotate(is_subscribed=Exists(subscriptions))
        return User.objects.all()

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
        detail=False,
    )
    def subscriptions(self, request):
        """
        Метод для обработки GET запросов на получение списка пользователей, на
        которых подписан текущий пользователь. В выдачу добавляются рецепты.
        URL - /users/subscriptions/.
        """

        user = request.user
        queryset = user.subscribing.annotate(
            is_subscribed=Exists(
                Subscribe.objects.filter(user=user, user_author=OuterRef('pk'))
            )
        ).prefetch_related('recipes').all()

        page = self.paginate_queryset(queryset)

        if page:
            serializer = self.get_serializer(page, many=True)

        serializer = self.get_serializer(queryset, many=True)

        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(CustomCreateDeleteMixin):
    """
    Вьюсет для работы с запросами о подписке на автора - добавление и
    удаление автора из списка подписок по id автора.
    URL - /users/<int:id>/subscribe/.
    """

    name = 'Обработка запросов на добавление/удаление автора в подписки'
    description = 'Обработка запросов на добавление/удаление автора в подписки'

    permission_classes = (IsAuthenticated,)
    model_class = User
    error = 'Указанный автор не был добавлен в ваши подписки.'

    def get_queryset(self):
        user = self.request.user
        return user.subscribing

    def get_serializer(self, id):
        return SubscribeSerializer(
            data={
                'user_author': id,
                'user': self.request.user.id,
                'type_list': 'shopping',
            },
            context={
                'request': self.request,
            }
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
            user = get_object_or_404(
                User, email=serializer.validated_data['email']
            )
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

    serializer_class = RecipeSerializer
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

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            favorite = user.favorite_recipes.filter(id=OuterRef('id'))
            shopping_list = user.shopping_recipes.filter(id=OuterRef('id'))
            return Recipe.objects.annotate(
                is_favorited=Exists(favorite),
                is_in_shopping_cart=Exists(shopping_list)
            )
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['GET', ],
        url_path='download_shopping_cart',
        detail=False,
    )
    def download_shopping_cart(self, request):
        """
        Метод для загрузки списка покупок в формате PDF.
        URL = recipes/download_shopping_cart/.
        """

        user = request.user
        ingredient_list_user = (
            IngredientInRecipe.objects.
            prefetch_related('ingredient', 'recipe').
            filter(recipe__shoppings=user).
            values('ingredient__id').
            order_by('ingredient__id')
        )

        shopping_list = (
            ingredient_list_user.annotate(amount=Sum('quantity')).
            values_list(
                'ingredient__name', 'ingredient__measurement_unit', 'amount'
            )
        )

        file = services.create_pdf(shopping_list, 'Список покупок')

        return FileResponse(
            file,
            as_attachment=True,
            filename='shopping_list.pdf',
            status=status.HTTP_200_OK
        )


class FavouriteViewSet(CustomCreateDeleteMixin):
    """
    Вьюсет для работы с запросами об избранном - добавление в избранное и
    удаление рецепта из избранного по id.
    URL - /recipes/<int:id>/favorite/.
    """

    name = 'Обработка запросов на добавление/удаление в избранное'
    description = 'Обработка запросов на добавление/удаление в избранное'

    permission_classes = (IsAuthenticated,)
    model_class = Recipe
    error = 'Указанный рецепт не был добавлен в список избранного.'

    def get_queryset(self):
        user = self.request.user
        return user.favorite_recipes

    def get_serializer(self, id):
        return FavoriteShoppingSerializer(
            data={
                'recipe': id,
                'user': self.request.user.id,
                'type_list': 'favorite',
            },
            context={
                'request': self.request,
            }
        )


class ShoppingListViewSet(CustomCreateDeleteMixin):
    """
    Вьюсет для работы с запросами о списке покупок - добавление в список и
    удаление рецепта из списка по id.
    URL - /recipes/<int:id>/shopping_cart/.
    """

    name = 'Обработка запросов на добавление/удаление в список покупок'
    description = 'Обработка запросов на добавление/удаление в список покупок'

    permission_classes = (IsAuthenticated,)
    model_class = Recipe
    error = 'Указанный рецепт не был добавлен в список покупок.'

    def get_queryset(self):
        user = self.request.user
        return user.shopping_recipes

    def get_serializer(self, id):
        return FavoriteShoppingSerializer(
            data={
                'recipe': id,
                'user': self.request.user.id,
                'type_list': 'shopping',
            },
            context={
                'request': self.request,
            }
        )
