from django.contrib import admin

from . import models


class TagAdmin(admin.ModelAdmin):
    model = models.Tag
    list_display = ['pk', 'name', 'color', 'slug']


class IngredientAdmin(admin.ModelAdmin):
    model = models.Ingredient
    list_display = ['pk', 'name', 'measurement_unit']


class IngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 1


class TagInline(admin.TabularInline):
    model = models.RecipeTag
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    model = models.Recipe
    inlines = (IngredientInline, TagInline)
    list_display = ['id', 'author',
                    'name', 'image',
                    'text', 'cooking_time'
                    ]


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
