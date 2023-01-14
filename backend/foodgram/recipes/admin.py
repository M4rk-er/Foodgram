from django.contrib import admin
from .models import Recipe, Ingredients, Tag, RecipeIngredients


class IngredientInline(admin.TabularInline):
    model = RecipeIngredients


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    ordering = ('pk',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'text', 'cooking_time')
    search_fields = ('author', 'name', 'recipe',)
    list_filter = ('name',)
    empty_value_display = 'пусто'
    inlines = (IngredientInline,)
    filter_horizontal = ('tag',)
    