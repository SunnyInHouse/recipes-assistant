from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework import status

from . models import Subscribe, User
from . serializers import UserCreateSerializer, UserSerializer, UserChangePasswordSerializer


class UserReadOnlyViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
        user = request.user
        serializer = self.get_serializer(user)
        return Response()

#  def set_password(self, request, pk=None):
#         user = self.get_object()
#         serializer = PasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             user.set_password(serializer.validated_data['password'])
#             user.save()
#             return Response({'status': 'password set'})
#         else:
#             return Response(serializer.errors,
#                             status=status.HTTP_400_BAD_REQUEST)


    @action(
        methods =['GET',],
        url_path = 'me',
        detail = False
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status = status.HTTP_200_OK)


