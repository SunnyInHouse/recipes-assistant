from rest_framework.serializers import ModelSerializer, SerializerMethodField, Serializer

from users.models import Subscribe, User

class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name','last_name',
            'is_subscribed',
        )
    
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscribers.filter(user_author=obj).exists()
        return False


class UserCreateSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('__all__')


class UserChangePasswordSerializer(Serializer):
    current_password=...
    new_password=...

