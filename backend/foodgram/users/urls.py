from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


router1 = DefaultRouter()

router1.register('', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(router1.urls)),
    # path(
    #     'token/login/',
    #     views.GetTokenView.as_view(),
    #     name='token_login'
    # ),
    # path(
    #     'token/logout/',
    #     views.DelTokenView.as_view(),
    #     name='token_logout'
    # ),
    path('token/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]