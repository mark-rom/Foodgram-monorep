from re import fullmatch
from typing import List

from django.db import transaction
from drf_base64.fields import Base64ImageField
from recipes import models
from rest_framework import serializers, status
from users.models import Subscription, User


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed'
                  ]

    def get_is_subscribed(self, obj):
        """Метод проверки наличия подписки на пользователя."""

        user = self.context['request'].user

        if user.is_authenticated:
            following = user.follower.all().values_list(
                'following_id', flat=True
            )

            return obj.pk in following

        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ['id', 'name', 'color', 'slug']

        def validate(self, data):
            """Проверка, что цвет представлен в формате HEX."""
            if not fullmatch('#[0-9A-F]{6}', data['color']):
                raise serializers.ValidationError('Цвет должен быть в HEX.')
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
        """Метод проверки наличия рецепта в избранном."""

        user = self.context['request'].user

        if user.is_authenticated:
            try:
                return obj.is_favorited
            except AttributeError:
                return models.Favorites.objects.filter(
                    recipe=obj, user=user
                ).exists()

        return False

    def get_is_in_shopping_cart(self, obj):
        """Метод проверки наличия рецепта в списке покупок."""

        user = self.context['request'].user

        if user.is_authenticated:
            try:
                return obj.is_in_shopping_cart
            except AttributeError:
                return models.ShoppingCart.objects.filter(
                    recipe=obj, user=user
                ).exists()

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
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=models.Recipe.objects.all(),
                fields=['name', 'text'],
                message='Рецепт с таким названием или текстом уже доступен.'
            )
        ]

    def _ingredietns_bulk_create(
        self, recipe: models.Recipe, ingredients: List
    ) -> None:

        bulk_list = [None] * len(ingredients)

        ingredients_ids = [ingredient.get('id') for ingredient in ingredients]
        ingredients_in_bulk = models.Ingredient.objects.in_bulk(
            ingredients_ids
        )

        for num, ingredient in enumerate(ingredients):
            if ingredient.get('id') not in ingredients_in_bulk:
                raise serializers.ValidationError(
                    f"Ингредиент с id: {ingredient.get('id')} не найден",
                    status.HTTP_400_BAD_REQUEST
                )

            new_instance = models.RecipeIngredient(
                recipe=recipe,
                ingredient=ingredients_in_bulk[ingredient.get('id')],
                amount=ingredient.get('amount')
            )
            bulk_list[num] = new_instance

        models.RecipeIngredient.objects.bulk_create(bulk_list)

    @transaction.atomic
    def create(self, validated_data):

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        new_recipe = super().create(validated_data)

        bulk_list = [None] * len(ingredients)

        self._ingredietns_bulk_create(new_recipe, ingredients)

        bulk_list = [None] * len(tags)
        tags = models.Tag.objects.in_bulk(tags)

        for num, tag in enumerate(tags.values()):
            new_instance = models.RecipeTag(
                recipe=new_recipe,
                tag=tag
            )
            bulk_list[num] = new_instance

        models.RecipeTag.objects.bulk_create(bulk_list)

        return new_recipe

    @transaction.atomic
    def update(self, instance, validated_data):

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.recipeingredient_related.all().delete()

        self._ingredietns_bulk_create(instance, ingredients)

        bulk_list = [None] * len(tags)
        tags = models.Tag.objects.in_bulk(tags)

        for num, tag in enumerate(tags.values()):
            bulk_list[num] = tag

        instance.tags.set(bulk_list)

        return super().update(
            instance=instance, validated_data=validated_data
        )

    def to_representation(self, value):

        serializer = ReadRecipeSerializer(value, context=self.context)
        return serializer.data

    def validate(self, attrs):

        try:
            ingredients = attrs['ingredients']
        except KeyError:
            raise serializers.ValidationError(
                'Не добавлены ингредиенты.'
            )

        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1.'
                )

        return super().validate(attrs)


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
                message='Рецепт уже в списке покупок.'
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
                message='Рецепт уже в избранном.'
            )
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):

    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = Subscription
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count'
                  ]

    def get_is_subscribed(self, obj):
        return obj.user == self.context['request'].user

    def get_recipes_count(self, obj):
        try:
            return obj.recipes_count
        except AttributeError:
            return models.Recipe.objects.filter(
                author=obj.following
            ).count()

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        if not recipes_limit:
            recipes = obj.following.recipes.all()
        else:
            recipes = obj.following.recipes.all()[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True, read_only=True).data


class SubscriptionSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    following = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ['user', 'following']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'following'],
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя')
        return data

    def to_representation(self, value):

        serializer = UserSubscriptionSerializer(value, context=self.context)
        return serializer.data
