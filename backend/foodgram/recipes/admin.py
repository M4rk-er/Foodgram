from django.contrib import admin
from .models import Recipe, Ingredient, Tag, IngredientInRecipe


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    ordering = ('pk',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('pk',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'text', 'cooking_time')
    search_fields = ('author', 'name', 'recipe',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = 'пусто'
    inlines = (IngredientInline,)
    filter_horizontal = ('tags',)
