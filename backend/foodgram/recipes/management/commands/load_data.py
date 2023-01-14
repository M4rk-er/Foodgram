from django.core.management.base import BaseCommand
from recipes.models import Ingredients
import csv

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('./static/data/ingredients.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                _, created = Ingredients.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
