from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import FileResponse, HttpResponse

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
    def shopping_cart(self, request):
        recipe = self.get_object()
        user = request.user

        if request.method == 'DELETE':
            shopping_cart_instance = get_object_or_404(models.ShoppingCart, recipe=recipe, user=user)
            shopping_cart_instance.delete()
            return HttpResponse()
        sh_c, content = models.ShoppingCart.objects.get_or_create(recipe=recipe, user=user)
        pass


class SubscribtionViewSet(BaseCreateDestroyViewSet):
    queryset = Subscribtion.objects.all()
    serializer_class = serializers.Subscribtion


class ShoppingCartViewSet(BaseCreateDestroyViewSet):
    serializer_class = serializers.ShoppingCartSerializer

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        return get_object_or_404(
            models.Recipe.objects.select_related('shoppingcart_related'),
            pk=recipe_id
        )
