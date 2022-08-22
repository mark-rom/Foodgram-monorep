import django_filters.rest_framework as filters

from recipes import models


class RecipeFilter(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=models.Tag.objects.all()
    )
    author = filters.CharFilter(
        field_name='author__username', lookup_expr='iexact'
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
