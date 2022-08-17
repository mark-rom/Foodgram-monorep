from re import fullmatch

from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes import models
from users.models import Subscribtion, User


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


class RecipeTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RecipeTag
        fields = ['tag']


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ['id', 'name', 'measurement_unit']


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):

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


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = models.RecipeIngredient
        fields = ['id', 'amount']


class ReadRecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = ReadRecipeIngredientSerializer(
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
        """Примерный вид функции вхождения в список избранного.
        Подлежит доработке."""

        user = self.context['request'].user

        if user.is_authenticated:
            return user.favorites_related.filter(recipe=obj).exists()

        return False

    def get_is_in_shopping_cart(self, obj):
        """Примерный вид функции вхождения в список покупок.
        Подлежит доработке."""

        user = self.context['request'].user

        if user.is_authenticated:
            return user.shoppingcart_related.filter(recipe=obj).exists()

        return False


class WriteRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()
    ingredients = WriteRecipeIngredientSerializer(many=True)
    tags = serializers.ListField()

    class Meta:
        model = models.Recipe
        fields = ['tags', 'ingredients', 'name', 'image', 'text',
                  'cooking_time'
                  ]

    def create(self, validated_data):

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        new_recipe = models.Recipe.objects.create(**validated_data)

        # Вот это нужно делать в одной "автономной" транзакции
        # также подумать над созданием объектов через bulk_create
        for ingredient in ingredients:
            models.RecipeIngredient.objects.create(
                recipe=new_recipe,
                ingredient=get_object_or_404(
                    models.Ingredient, id=ingredient.get('id')
                ),
                amount=ingredient.get('amount')
            )

        for tag in tags:
            models.RecipeTag.objects.create(
                recipe=new_recipe,
                tag=get_object_or_404(models.Tag, id=tag)
            )
        # Вот до сюда

        return new_recipe

    def update(self, instance, validated_data):

        tag_list = []
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        # Вот это нужно делать в одной "автономной" транзакции
        # также подумать над созданием объектов через bulk_create
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        recipe_ingredients = instance.recipeingredient_related.all()
        recipe_ingredients.delete()

        for ingredient in ingredients:
            models.RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=get_object_or_404(
                    models.Ingredient, id=ingredient.get('id')
                ),
                amount=ingredient.get('amount')
            )

        for tag in tags:
            new_tag = get_object_or_404(models.Tag, id=tag)
            tag_list.append(new_tag)

        instance.tags.set(tag_list)
        # Вот до сюда

        return instance

    def to_representation(self, value):

        serializer = ReadRecipeSerializer(value, context=self.context)
        return serializer.data


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ShoppingCart
        fields = ['user', 'recipe']

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=models.ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='The recipe is in the shopping cart already.'
            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Favorites
        fields = ['user', 'recipe']

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=models.Favorites.objects.all(),
                fields=['user', 'recipe'],
                message='The recipe is in favorites already.'
            )
        ]
