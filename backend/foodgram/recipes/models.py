from re import fullmatch

from django.core.exceptions import ValidationError
from django.db import models
from users.models import User


class Tag(models.Model):

    name = models.CharField(
        max_length=30, blank=False,
        null=False, verbose_name='Название',
        unique=True
    )
    color = models.CharField(
        max_length=10, blank=False,
        null=False, verbose_name='Цвет в формате HEX'
    )
    slug = models.SlugField(
        blank=False, null=False,
        unique=True,
    )

    class Meta:
        verbose_name = ('Тег')
        verbose_name_plural = ('Теги')

    def __str__(self):
        return self.name

    def clean(self) -> None:
        if not fullmatch('#[0-9A-Fa-f]{6}', self.color):
            raise ValidationError('Цвет должен быть в HEX.')


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
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):

    tags = models.ManyToManyField(
        Tag, through='RecipeTag',
        blank=False,
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
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        blank=False,
        verbose_name='Ингредиенты'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=False, null=False,
        verbose_name='Автор',
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = ('Рецепт')
        verbose_name_plural = ('Рецепты')
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'text'],
                name='unique_name_text_recipe'
            )
        ]

    def __str__(self):
        return self.name


class BaseRecipeLinkTable(models.Model):
    """Base class containing recipe field with description."""
    recipe = models.ForeignKey(
        Recipe,
        blank=False, null=False,
        on_delete=models.CASCADE,
        related_name="%(class)s_related"
    )

    class Meta:
        abstract = True


class BaseRecipeUser(BaseRecipeLinkTable):
    """Base class inherited from BaseRecipeLinkTable class.
    Class contains description of user field."""
    user = models.ForeignKey(
        User,
        blank=False, null=False,
        on_delete=models.CASCADE,
        related_name="%(class)s_related"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} {self.recipe}'


class RecipeTag(BaseRecipeLinkTable):

    tag = models.ForeignKey(
        Tag,
        blank=False, null=True,
        on_delete=models.SET_NULL,
        related_name='recipes'
    )

    class Meta:
        verbose_name = ('Тег рецепта')
        verbose_name_plural = ('Теги рецептов')

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(BaseRecipeLinkTable):

    ingredient = models.ForeignKey(
        Ingredient,
        blank=False, null=False,
        on_delete=models.CASCADE,
        related_name='recipes'
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shopping_cart'
            )
        ]


class Favorites(BaseRecipeUser):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorites'
            )
        ]
