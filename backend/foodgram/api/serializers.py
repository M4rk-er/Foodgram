from rest_framework import serializers
from users.models import User
from recipes.models import Recipe, Tag, Ingredients, RecipeIngredients


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User(
            email = validated_data['email'],
            username = validated_data['username'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
        
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)

    def validate(self, attrs):
        if attrs['new_password'] == attrs['current_password']:
            raise serializers.ValidationError({'status': 'Поля не должны совпадать'})
        return attrs


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',
        )


class GetIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиента для получения рецепта.'''
    id = serializers.SerializerMethodField(method_name='get_id')
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(method_name='get_measurement_unit')
    amount = serializers.SerializerMethodField(method_name='get_amount')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredients.id

    def get_name(self, obj):
        return obj.ingredients.name

    def get_measurement_unit(self, obj):
        return obj.ingredients.measurement_unit

    def get_amount(self, obj):
        return obj.amount


class RecipeCreateIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор создания ингредиентов в рецепте.'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        required=True,
        source='ingredients'
    )
    amount = serializers.IntegerField(
        required=True
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount',)


class GetRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор получения рецепта.'''
    tag = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = GetIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    # is_favorite = serializers.SerializerMethodField(method_name='get_favorite')
    # is_in_shopping_cart = serializers.SerializerMethodField(method_name='get_card')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tag',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time',
        )


    
    
class CreateRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор создания рецепта.'''
    ingredients = RecipeCreateIngredientSerializer(many=True, required=True)
    tag = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tag',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        tag_data = validated_data.pop('tag')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tag_data:
            recipe.tag.add(tag)
        recipe.save()
        for ingredient in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredients=ingredient['ingredients'],
                amount=int(ingredient.pop('amount'))
            )
        return recipe
