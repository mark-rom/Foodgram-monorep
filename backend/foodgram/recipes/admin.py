from django.contrib import admin

from . import models


class TagAdmin(admin.ModelAdmin):
    model = models.Tag
    list_display = ['pk', 'name', 'color', 'slug']


class IngredientAdmin(admin.ModelAdmin):
    model = models.Ingredient
    list_display = ['pk', 'name', 'measurement_unit']


class RecipeAdmin(admin.ModelAdmin):
    model = models.Recipe
    list_display = ['id', 'author',
                    'name', 'image',
                    'text', 'cooking_time'
                    ]


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
