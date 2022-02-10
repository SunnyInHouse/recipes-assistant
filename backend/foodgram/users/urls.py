from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router1 = DefaultRouter()

router1.register('', views.UserViewSet, basename = 'users')

urlpatterns = [
    path('', include(router1.urls) )
]