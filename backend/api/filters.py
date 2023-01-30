from django_filters import FilterSet, CharFilter

from recipes.models import Ingredient

class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)