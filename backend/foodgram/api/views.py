from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from recipes import models
from users.models import User, Subscribtion
from api import serializers


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
    queryset = models.Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.ReadRecipeSerializer
        return serializers.WriteRecipeSerializer


class SubscribtionViewSet(BaseCreateDestroyViewSet):
    queryset = Subscribtion.objects.all()
    serializer_class = serializers.Subscribtion
