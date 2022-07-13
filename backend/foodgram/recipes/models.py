from django.db import models

from ..users.models import User


class Tag(models.Model):

    name = models.CharField(
        max_length=30, blank=False,
        null=False, verbose_name='Название'
    )
    color = models.CharField(blank=False, null=False,)
    # поле color можно реализовать с помощью стороннего модуля на HexField
    slug = models.SlugField(
        blank=False, null=False,
        unique=True,
    )

    class Meta:
        verbose_name = ('Тег')
        verbose_name_plural = ('Теги')

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        max_length=100, blank=False,
        null=False, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=50, blank=False,
        null=False, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = ('Ингредиент')
        verbose_name_plural = ('Ингредиенты')

    def __str__(self):
        return self.name


class Recipe(models.Model):

    tags = models.ManyToManyField(
        Tag, through='RecipeTag',
        blank=False, null=False,
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False, null=False,
        verbose_name='Изображение'
    )
    name = models.CharField(
        max_length=200, blank=False, null=False,
        verbose_name='Название'
    )
    text = models.TextField(
        blank=False, null=False,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        blank=False, null=False,
        verbose_name='Время приготовления (в минутах)'
        # можно ли на уровне модели ограничить используемые числа?
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        blank=False, null=False,
        verbose_name='Ингредиенты'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=False, null=False,
        verbose_name='Теги'
    )
    is_favorited = models.ManyToManyField(
        User, through='Favorites',
        verbose_name='Избранное'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User, through='ShoppingCart',
        verbose_name='Список покупок'
    )

    class Meta:
        verbose_name = ('Рецепт')
        verbose_name_plural = ('Рецепты')

    def __str__(self):
        return self.name


class BaseRecipeLink(models.Model):
    """Base class containing recipe field with description."""
    recipe = models.ForeignKey(
        Recipe,
        blank=False, null=False,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class BaseRecipeUser(BaseRecipeLink):
    """Base class inherited from BaseRecipeLink class.
    Class contains description of user field."""
    user = models.ForeignKey(
        User,
        blank=False, null=False,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} {self.recipe}'


class RecipeTag(BaseRecipeLink):

    tag = models.ForeignKey(
        Tag,
        blank=False, null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = ('Тег рецепта')
        verbose_name_plural = ('Теги рецептов')

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(BaseRecipeLink):

    ingredient = models.ForeignKey(
        Ingredient,
        blank=False, null=False,
        on_delete=models.PROTECT
    )
    amount = models.PositiveSmallIntegerField(blank=False, null=False,)

    class Meta:
        verbose_name = ('Ингредиент рецепта')
        verbose_name_plural = ('Ингредиенты рецептов')

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class ShoppingCart(BaseRecipeUser):

    class Meta:
        verbose_name = ('Список покупок')
        verbose_name_plural = ('Списки покупок')


class Favorites(BaseRecipeUser):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
