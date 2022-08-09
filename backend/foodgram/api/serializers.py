from re import fullmatch
from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from recipes import models
from users.models import User, Subscribtion


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribtion
        fields = ['user', 'following']


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed'
                  ]

    def get_is_subscribed(self, obj):

        # текущий пользователь
        user = self.context['request'].user

        if user.is_authenticated:
            # queryset со всеми авторами, на которых подписан юзер
            following = user.following.all().values('id')
            return obj.pk in following

        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ['id', 'name', 'color', 'slug']

        def validate(self, data):
            """Check if color is HEX-color"""
            if not fullmatch('#[0-9A-F]{6}', data['color']):
                raise serializers.ValidationError('Color must be HEX-color')
            return data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = models.RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class ReadRecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source='recipeingredient_related'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = models.Recipe
        fields = ['id', 'tags', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time'
                  ]

    def get_is_favorited(self, obj):

        # текущий пользователь
        user = self.context['request'].user

        if user.is_authenticated:
            # queryset со всеми избранными рецептами юзера
            favorites = models.Favorites.objects.filter(
                user=user.pk).values('recipe')
            return obj.pk in favorites

        return False

    def get_is_in_shopping_cart(self, obj):

        # текущий пользователь
        user = self.context['request'].user

        if user.is_authenticated:
            # queryset со всеми избранными рецептами юзера
            cart = models.ShoppingCart.objects.filter(
                user=user.pk).values('recipe')
            return obj.pk in cart

        return False


class WriteRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = ['id', 'tags', 'author',
                  'ingredients', 'name', 'image',
                  'text', 'cooking_time'
                  ]

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        new_recipe = models.Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            # добавить проверку на наличие ингредиента в бд
            models.RecipeIngredient.objects.create(
                recipe=new_recipe.pk,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        for tag in tags:
            models.RecipeTag.objects.create(
                recipe=new_recipe.pk,
                tag=tag
            )
        return new_recipe
