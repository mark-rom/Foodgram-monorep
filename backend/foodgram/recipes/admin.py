from django.contrib import admin

from . import models


class TagAdmin(admin.ModelAdmin):
    model = models.Tag
    list_display = ['pk', 'name', 'color', 'slug']


class IngredientAdmin(admin.ModelAdmin):
    model = models.Ingredient
    list_display = ['pk', 'name', 'measurement_unit']
    search_fields = ['name']


class IngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 1


class TagInline(admin.TabularInline):
    model = models.RecipeTag
    extra = 1


class ShoppingCartInlite(admin.TabularInline):
    model = models.ShoppingCart
    extra = 1


class FavoritesInlite(admin.TabularInline):
    model = models.Favorites
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    model = models.Recipe
    inlines = (
        IngredientInline, TagInline,
        ShoppingCartInlite, FavoritesInlite
    )
    list_display = ['id', 'author',
                    'name', 'image',
                    'text', 'cooking_time'
                    ]
    list_filter = ['author', 'name', 'tags']


class ShoppongCartAdmin(admin.ModelAdmin):
    model = models.ShoppingCart
    list_display = ['id', 'user', 'recipe']


class FavoritesAdmin(admin.ModelAdmin):
    model = models.Favorites
    list_display = ['id', 'user', 'recipe']


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.ShoppingCart, ShoppongCartAdmin)
admin.site.register(models.Favorites, FavoritesAdmin)
