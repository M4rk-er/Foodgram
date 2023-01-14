from django.db import models

from users.models import User

from .validators import slug_validation


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Имя',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        blank=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        validators=[slug_validation],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )
    

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=200,
    )
    text = models.CharField(
        'Описание',
        max_length = 1000,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name = 'Автор'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        related_name='ingredients',
        verbose_name='Ингредиенты'
    )
    is_favorite = models.BooleanField(
        'В избранном',
        blank=True,
        default=False,
    )
    is_in_shopping_cart = models.BooleanField(
        'В корзине',
        blank=True,
        default=False,
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
    )


    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


# class RecipeTag(models.Model):
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#     )
#     tag = models.ForeignKey(
#         Tag,
#         on_delete=models.CASCADE
#     )

class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe, 
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиенты',
    )
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

