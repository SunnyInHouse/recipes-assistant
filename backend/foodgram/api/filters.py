from django_filters import rest_framework as filters
from rest_framework.serializers import ValidationError

from recipes.models import Recipe

from .services import check_value_is_0_or_1


class RecipeFilter(filters.FilterSet):
    """
    Набор фильтров для получения списка рецептов согласно заданным в
    query_param фильтрам. Доступна фильтрация по избранному, автору, списку
    покупок и тегам.
    """
    author = filters.NumberFilter(field_name='author__id', lookup_expr='exact')
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='in')
    is_favorited = filters.NumberFilter(method='filter_recipes')
    is_in_shopping_cart = filters.NumberFilter(method='filter_recipes')

    def filter_recipes(self, queryset, name, value):
        """
        Фильтрация рецептов по избранному и списку покупок. Также проверяет
        корректность заданного значения.
        """
        if not check_value_is_0_or_1(value):
            raise ValidationError(
                f"Некорректное значение параметра {name}."
            )
        user = self.request.user
        if user.is_authenticated:
            if value == 1:
                if name == 'is_favorited':
                    return queryset.filter(favorites__user=user)
                if name == 'is_in_shopping_cart':
                    return queryset.filter(shoppings__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
