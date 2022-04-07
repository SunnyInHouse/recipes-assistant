"""
Описания классов фильтрации.
"""

from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag

RECIPE_CHOICES = (
    (0, 'Not_In_List'),
    (1, 'In_List'),
)


class RecipeFilter(filters.FilterSet):
    """
    Набор фильтров для получения списка рецептов согласно заданным в
    query_param фильтрам. Доступна фильтрация по избранному, автору, списку
    покупок и тегам.
    """

    author = filters.NumberFilter(field_name='author__id', lookup_expr='exact')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=RECIPE_CHOICES,
        method='get_is_in'
    )
    is_favorited = filters.ChoiceFilter(
        choices=RECIPE_CHOICES,
        method='get_is_in'
    )

    def get_is_in(self, queryset, name, value):
        """
        Фильтрация рецептов по избранному и списку покупок.
        """
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                if name == 'is_favorited':
                    queryset = queryset.filter(favorites=user)
                if name == 'is_in_shopping_cart':
                    queryset = queryset.filter(shoppings=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
