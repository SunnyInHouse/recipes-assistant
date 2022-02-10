from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework import status

from . models import Subscribe, User
from . serializers import UserCreateSerializer, UserSerializer, UserChangePasswordSerializer


class UserViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet,
):
    """
    Вьюсет для работы с пользователями.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
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
        пользователем, запрос на /users/set_password.
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
        пользователя, запрос на /users/me.
        """
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status = status.HTTP_200_OK)


