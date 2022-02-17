from urllib import request
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import Subscribe, User
from .serializers import (GetTokenSerializer, ListSubscriptionsSerializer,
                          UserChangePasswordSerializer, UserSerializer)
from foodgram.pagination import CustomPageNumberPagination


class UserViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin,
                  GenericViewSet):
    """
    Вьюсет для работы с пользователями.
    URL - /users/.
    """

    name = 'Обработка запросов о пользователях'
    description = 'Обработка запросов о пользователях'
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    lookup_field = 'id'
    pagination_class = CustomPageNumberPagination
    

    def get_serializer_class(self):
        if self.action == 'set_password':
            return UserChangePasswordSerializer
        if self.action == 'subscriptions':
            return ListSubscriptionsSerializer
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
    def subscriptions(self,request):
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
                status=status.HTTP_200_OK
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

    def post(self, request):
        """
        Функция для обработки POST запроса, удаляет токен аутентификации.
        """
        token = request.auth
        token.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# class ListSubscriptions(ListModelMixin, GenericViewSet):
#     """
#     Класс для обработки GET запросов на получение пользователей, на которых
#     подписан текущий пользователь. В выдачу добавляются рецепты.
#     URL - /users/subscriptions/.
#     """

#     name = 'Получение списка подписок'
#     description = 'Получение списка подписок'


#     # serializer_class = ListSubscriptionsSerializer
#     queryset = Subscribe.objects.all()

#     # def get_queryset(self):
#     #     user=request.user
#     #     print(user)
#     #     return Subscribe.objects.all()
    
#     def list(self, request):
#         # serializer = self.get_serializer(request)
#         # if serializer.is_valid():
#         #     return Response(serializer.data)
#         return Response(status=status.HTTP_200_OK)
