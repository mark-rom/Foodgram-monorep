from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins, response, status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import FileResponse
from django.core.exceptions import ObjectDoesNotExist

from recipes import models
from users.models import User, Subscribtion
from api import serializers
from api.shopping_list_pdf import get_pdf


class BaseListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    pass


class BaseCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    pass


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class TagViewSet(BaseListRetrieveViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseListRetrieveViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = models.Recipe.objects.prefetch_related(
        'ingredients', 'tags'
    ).all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.ReadRecipeSerializer
        return serializers.WriteRecipeSerializer

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

        except ObjectDoesNotExist:
            return response.Response(
                {"no_recipe": "Вы не доавляли этот рецепт"},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        user = request.user

        # queryset of dicts | название, ед. измер. и количество
        # всех уникальных ингредиентов из корзины пользователя
        shopping_list = user.shoppingcart_related.values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit',
        ).annotate(
            ingredient_amount=Sum(
                'recipe__recipeingredient_related__amount',
                distinct=True
            )
        )
        byte_pdf = get_pdf(shopping_list)

        return FileResponse(
            byte_pdf, as_attachment=True,
            filename='shopping_list', content_type='application/pdf'
        )

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):

        recipe = get_object_or_404(models.Recipe, id=pk)
        user = request.user

        if request.method == 'DELETE':
            return self.__remove_recipe(recipe, user.shoppingcart_related)

        return self.__add_recipe(
            recipe, user, serializers.ShoppingCartSerializer
        )

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):

        recipe = get_object_or_404(models.Recipe, id=pk)
        user = request.user

        if request.method == 'DELETE':
            return self.__remove_recipe(recipe, user.favorites_related)

        return self.__add_recipe(
            recipe, user, serializers.FavoriteSerializer
        )


class SubscribtionViewSet(BaseCreateDestroyViewSet):
    queryset = Subscribtion.objects.all()
    serializer_class = serializers.Subscribtion
