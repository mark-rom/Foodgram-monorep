from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from recipes.models import Tag, Ingredient, Recipe
from users.models import User
from .serializers import (TagSerializer, IngredientSerializer,
                          GetRecipeSerializer, WriteRecipeSerializer,
                          UserSerializer
                          )


class BaseListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    pass


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagViewSet(BaseListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return WriteRecipeSerializer
