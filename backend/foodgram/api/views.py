from django.db.models import Count, Exists, OuterRef, Sum, Value
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes import models
from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from users.models import Subscription, User

from . import permissions, serializers
from .filters import IngredientSearchFilter, RecipeFilter
from .shopping_list_pdf import get_shopping_list


class BaseListRetrieveViewSet(
    ListModelMixin, RetrieveModelMixin,
    GenericViewSet
):
    pass


class FoodgramUserViewSet(UserViewSet):
    """Вьюсет для работы с эндпоинтом /users/ и производными."""

    @action(
        methods=['get'], detail=False,
        filter_backends=[DjangoFilterBackend],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Метод получения списка интересующих авторов."""

        user_following_qs = request.user.follower.all().annotate(
            recipes_count=Count('following__recipes')
        )
        qs = self.paginate_queryset(user_following_qs)
        serializer = serializers.UserSubscriptionSerializer(
            qs, many=True,
            context={
                'request': self.request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post'], detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Метод подписки на автора или отписки."""

        serializer = serializers.SubscriptionSerializer(
            data={'following': id}, context={'request': self.request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def subscribe_delete(self, request, id):

        following = get_object_or_404(User, pk=id)

        instance = Subscription.objects.filter(
            user=request.user, following=following
        )

        if instance.exists():

            instance.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)

        return response.Response(
            {"error": "Вы не были подписаны на этого пользователя"},
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(BaseListRetrieveViewSet):
    """Вьюсет для работы с эндпоинтом /tags/ и производными."""

    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


class IngredientViewSet(BaseListRetrieveViewSet):
    """Вьюсет для работы с эндпоинтом /ingredients/ и производными.
    Реализован поиск по вхождению в начало названия."""

    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientSearchFilter


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с эндпоинтом /recipes/ и производными.
    Реализована пагинация, пермишены, фильтр по автору, тегам,
    нахождению в списке покупок или избранном."""

    permission_classes = [
        IsAuthenticatedOrReadOnly,
        permissions.AuthorOrReadOnly,
    ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):

        user = self.request.user

        if user.is_anonymous:
            return models.Recipe.objects.select_related(
                'author'
            ).prefetch_related(
                'ingredients', 'tags'
            ).annotate(
                is_favorited=Value(False),
                is_in_shopping_cart=Value(False)
            ).all()

        is_favorited_qs = models.Favorites.objects.filter(
            user=user,
            recipe_id=OuterRef('pk')
        )
        shopping_cart_qs = models.ShoppingCart.objects.filter(
            user=user,
            recipe_id=OuterRef('pk')
        )

        return models.Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'ingredients', 'tags'
        ).annotate(
            is_favorited=Exists(is_favorited_qs),
            is_in_shopping_cart=Exists(shopping_cart_qs)
        ).all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.ReadRecipeSerializer
        return serializers.WriteRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def __add_recipe(self, recipe, user, serializer):
        """Базовый метод для добавления рецепта в корзину или избранное."""

        serializer = serializer(data={'user': user.id, 'recipe': recipe.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(recipe=recipe, user=user)

        serializer = serializers.ShortRecipeSerializer(recipe)

        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def __remove_recipe(self, recipe, related_manager):
        """Базовый метод для удаления рецепта из корзины или избранного."""

        try:
            instance = related_manager.get(recipe=recipe)

        except models.Recipe.DoesNotExist:
            return response.Response(
                {"no_recipe": "Вы не доавляли этот рецепт"},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'], detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Метод для получения списке рецептов в формате PDF."""

        user = request.user

        shopping_list = user.shoppingcart_related.values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit',
        ).annotate(
            ingredient_amount=Sum(
                'recipe__recipeingredient_related__amount',
                distinct=True
            )
        )

        bytes_file = get_shopping_list(shopping_list)

        return FileResponse(
            bytes_file, as_attachment=True, filename='shopping_list.pdf'
        )

    @action(
        methods=['post', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Метод добавления рецептов в список покупок и удаления из него."""

        recipe = get_object_or_404(models.Recipe, id=pk)
        user = request.user

        if request.method == 'DELETE':
            return self.__remove_recipe(recipe, user.shoppingcart_related)

        return self.__add_recipe(
            recipe, user, serializers.ShoppingCartSerializer
        )

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Метод добавления избранных рецептов и их удаления."""

        recipe = get_object_or_404(models.Recipe, id=pk)
        user = request.user

        if request.method == 'DELETE':
            return self.__remove_recipe(recipe, user.favorites_related)

        return self.__add_recipe(
            recipe, user, serializers.FavoriteSerializer
        )
