from re import fullmatch
from rest_framework.serializers import (ModelSerializer, ValidationError,
                                        SerializerMethodField
                                        )

from recipes import models
from users.models import User, Subscribtion


class SubscriptionSerializer(ModelSerializer):

    class Meta:
        model = Subscribtion
        fields = ['user', 'following']


class UserSerializer(ModelSerializer):

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed'
                  ]

    def get_is_subscribed(self, obj):

        # текущий пользователь
        user = self.context['request'].user

        # queryset со всеми авторами, на которых подписан юзер
        following = user.following.all().values('id')
        return obj.id in following


class TagSerializer(ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ['id', 'name', 'color', 'slug']

        def validate(self, data):
            """Check if color is HEX-color"""
            if not fullmatch('#[0-9A-F]{6}', data['color']):
                raise ValidationError('Color must be HEX-color')
            return data


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ['id', 'name', 'measurement_unit']


class GetRecipeSerializer(ModelSerializer):

    class Meta:
        model = models.Recipe
        fields = ['id', 'tags', 'author',
                  'ingredients', 'name', 'image',
                  'text', 'cooking_time'
                  ]


class WriteRecipeSerializer(ModelSerializer):

    class Meta:
        model = models.Recipe
        fields = ['id', 'tags', 'author',
                  'ingredients', 'name', 'image',
                  'text', 'cooking_time'
                  ]
