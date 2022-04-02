from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('users', views.UserViewSet, basename='users')
router.register(
    'users/(?P<id>[^/.]+)/subscribe',
    views.SubscribeViewSet,
    basename='subscribe'
)
router.register('tags', views.TagViewset, basename='tag')
router.register('ingredients', views.IngredientViewset, basename='ingredient')
router.register('recipes', views.RecipeViewset, basename='recipe')
router.register(
        'recipes/(?P<id>[^/.]+)/favorite',
        views.FavouriteViewSet,
        basename='favorite'
)
router.register(
    'recipes/(?P<id>[^/.]+)/shopping_cart',
    views.ShoppingListViewSet,
    basename='shoppinglist'
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'auth/token/login/',
        views.GetTokenView.as_view(),
        name='token_login'
    ),
    path(
        'auth/token/logout/',
        views.DelTokenView.as_view(),
        name='token_logout'
    ),
]
