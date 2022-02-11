from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework import status

from . models import Subscribe, User
from . serializers import (
    UserSerializer,
    UserChangePasswordSerializer,
    GetTokenSerializer,
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


class GetTokenView(APIView):
    """
    Класс для обработки POST запросов для получения токена авторизации по email
    и паролю.
    URL - /auth/token/login/.
    """

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        return Response(status = status.HTTP_200_OK)
   


class DelTokenView(APIView):
    """
    Класс для обработки POST запросов для удаления токена авторизации текущего
    пользователя.
    URL - /auth/token/logout/.
    """

    def post(self, request):
        ...
    pass