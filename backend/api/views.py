from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Follow, User

from .filters import IngredientFilter
from .pagination import CustomPagination
from .permissions import CustomUserPermissions, IsAuthor, IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FollowSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          PasswordSerializer, RecipeFavoriteSerializer,
                          TagSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = (CustomUserPermissions,)
    http_method_names = ['get', 'post', 'delete']

    @action(
        detail=False, methods=['get'],
        url_name='me', url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def current_user_information(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, methods=['post'],
        url_name='set_password', url_path='set_password',
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        user = get_object_or_404(User, username=request.user)
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.data['current_password']):
            return Response({'status': 'Текцщий пароль указан неверно'})
        user.set_password(serializer.data['new_password'])
        user.save()
        return Response(
            {'status': 'Пароль изменен'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True, methods=['post', 'delete'],
        url_name='subscribe', url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serilalizer = FollowSerializer(
                author, data=request.data, context={'request': request}
            )
            serilalizer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serilalizer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            follow = get_object_or_404(Follow, user=user, author=author)
            self.perform_destroy(follow)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'], url_name='subscriptions',
        url_path='subscriptions', detail=False,
        permission_classes=(IsAuthor,)
    )
    def subscriptions(self, request):
        follows = User.objects.filter(following__user=self.request.user)
        paginate_follows = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            paginate_follows,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetRecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user

        is_favorited = self.request.query_params.get('is_favorited')
        favorited = FavoriteRecipe.objects.filter(user=user)
        if is_favorited == '1':
            queryset = queryset.filter(favoriterecipe__in=favorited)
        if is_favorited == '0':
            queryset = queryset.exclude(favoriterecipe__in=favorited)

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        shopping_cart = ShoppingCart.objects.filter(user=user)
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(shopping_cart__in=shopping_cart)
        if is_in_shopping_cart == '0':
            queryset = queryset.exclude(shopping_cart__in=shopping_cart)

        tags = self.request.query_params.getlist('tags')
        if tags is not None:
            slug = Tag.objects.filter(slug__in=tags).all()
            recipes = Recipe.objects.filter(tags__in=slug).values('id').distinct()
            queryset = queryset.filter(id__in=recipes)

        author_id = self.request.query_params.get('author')
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id).all()

        return queryset

    @action(
        detail=True, methods=['post', 'delete'],
        url_name='favorite', url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeFavoriteSerializer(recipe)
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
                FavoriteRecipe.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True, methods=['post', 'delete'],
        url_name='shopping_cart', url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_card(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeFavoriteSerializer(recipe)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                ShoppingCart.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт не был добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'],
        url_name='download_shopping_cart', url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        queryset = (
            ShoppingCart.objects.filter(user=user)
            .values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit'
            )
            .annotate(Sum('recipe__ingredientinrecipe__amount'))
            .order_by('recipe__ingredients__name')
        )

        shopping_list = ['Список покупок:\n\n']
        for item in queryset:
            name = item['recipe__ingredients__name'].capitalize()
            measurement_unit = item['recipe__ingredients__measurement_unit']
            amount = item['recipe__ingredientinrecipe__amount__sum']
            shopping_list.append(f'{name} ({measurement_unit}) — {amount};\n')

        response = HttpResponse(shopping_list)
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response
