from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response

from recipes.models import Tag, Ingredients, Recipe
from users.models import User

from .serializers import TagSerializer, UserSerializer, PasswordSerializer, GetIngredientSerializer, GetRecipeSerializer, CreateRecipeSerializer
from .permissions import UserPermissions


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (UserPermissions,)

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
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(serializer.data['current_password']):
            return Response({'status':'Текцщий пароль указан неверно'})
        user.set_password(serializer.data['new_password'])
        user.save()
        return Response(
            {'status': 'Пароль изменен'},
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = GetIngredientSerializer
    

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
