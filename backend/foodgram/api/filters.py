import django_filters.rest_framework as filters

from recipes import models


class RecipeFilter(filters.FilterSet):
    """Фильр для вьюсета рецептов.
    Реализована фильтрация по id автора, тегам рецепта,
    нахождению рецепта в избранном или списке покупок.
    """

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=models.Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        return queryset.filter(favorites_related__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(shoppingcart_related__user=self.request.user)

    class Meta:
        model = models.Recipe
        fields = ['author']


class IngredientSearchFilter(filters.FilterSet):
    """Фильр для вьюсета ингредиентов.
    Реализована фильтрация по точному вхождению в начало названия.
    """

    name = filters.CharFilter(
        field_name="name", lookup_expr='istartswith'
    )

    class Meta:
        model = models.Ingredient
        fields = ('name',)
