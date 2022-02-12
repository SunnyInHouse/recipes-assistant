from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from . models import Subscribe, User
from . serializers import (
    UserSerializer,
    UserChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)


class UserViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet,
):
    """
    Вьюсет для работы с пользователями.
    URL - /users/.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me', 'create'):
            return UserSerializer
        if self.action == 'set_password':
            return UserChangePasswordSerializer
        return UserCreateSerializer

    @action(
        methods =['POST',],
        url_path = 'set_password',
        detail = False
    )
    def set_password(self, request):
        """
        Метод для обработки запроса POST на изменение пароля авторизованным
        пользователем.
        URL - /users/set_password.
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods =['GET',],
        url_path = 'me',
        detail = False
    )
    def me(self, request):
        """
        Метод для обработки запроса GET на получение данных профиля текущего
        пользователя.
        URL - /users/me.
        """
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status = status.HTTP_200_OK)


# class GetTokenView(APIView):
#     """
#     Класс для обработки POST запросов для получения токена авторизации по email
#     и паролю.
#     URL - /auth/token/login/.
#     """

#     def post(self, request):
#         serializer = GetTokenSerializer(data=request.data)
#         if serializer.is_valid():
#             # создание токена и отдать в response
#             return Response(status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Класс для обработки POST запросов для получения jwt токена авторизации по
    email и паролю. 
    Унаследован от стандартного класса библиотеки rest_framework_simplejwt - 
    views.TokenObtainPairView.
    URL - /auth/token/login/.
    """

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(
                serializer.validated_data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DelTokenView(APIView):
    """
    Класс для обработки POST запросов для удаления токена авторизации текущего
    пользователя.
    URL - /auth/token/logout/.
    """

    authentication_classes = []

    def post(self, request):
        # удаление токена - добавление в блэклист
        return Response(status=status.HTTP_204_NO_CONTENT)
