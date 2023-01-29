from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.validators import ValidationError

from users.models import Follow, User
from recipes.models import (FavoriteRecipe, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации/получения информации пользователя."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class PasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)

    def validate(self, value):
        if value['new_password'] == value['current_password']:
            raise serializers.ValidationError(
                {'status': 'Поля не должны совпадать'})
        return value


class FollowSerializer(UserSerializer):
    """Сериализатор подписки/отписки на пользователя."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        model = User
        read_only_fields = ('email', 'username', 'first_name', 'last_name',)

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)[:6]
        serializer = RecipeFavoriteSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj).count()
        return recipes

    def validate(self, value):
        user = self.context['request'].user
        author = self.instance
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого автора',
                code=status.HTTP_400_BAD_REQUEST
            )
        if author == user:
            raise ValidationError(
                detail='Нельзя подпиываться на себя',
                code=status.HTTP_400_BAD_REQUEST
            )

        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор получения информации об ингредиенте."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор получения информации о теге."""
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',
        )


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецепта при добавление в избранное."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создание ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True,
        source='ingredients'
    )
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения ингредиента из рецепта."""
    id = serializers.SerializerMethodField(method_name='get_id')
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(
        method_name='get_measurement_unit'
    )
    amount = serializers.SerializerMethodField(method_name='get_amount')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredients.id

    def get_name(self, obj):
        return obj.ingredients.name

    def get_measurement_unit(self, obj):
        return obj.ingredients.measurement_unit

    def get_amount(self, obj):
        return obj.amount


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = GetIngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredientinrecipe_set'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_basket'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_basket(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""
    ingredients = CreateIngredientInRecipeSerializer(
        many=True, required=True, source='ingredientinrecipe_set'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        tag_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredientinrecipe_set')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tag_data)
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredients=ingredient.get('ingredients'),
                amount=int(ingredient.pop('amount'))
            ) for ingredient in ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredientinrecipe_set' in validated_data:
            instance.ingredients.all().delete()
            ingredients_data = validated_data.get('ingredientinrecipe_set')
            IngredientInRecipe.objects.bulk_create(
                IngredientInRecipe(
                    recipe=instance,
                    ingredients=ingredient.get('ingredients'),
                    amount=int(ingredient.pop('amount'))
                ) for ingredient in ingredients_data)

        if 'tags' in validated_data:
            instance.tags.set(validated_data['tags'])

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        return instance
