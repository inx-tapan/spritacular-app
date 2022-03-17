from django.core.management.base import BaseCommand
from observation.models import Category


class Command(BaseCommand):
    help = 'This class is for populating the categories list in the observation form.'

    def handle(self, *args, **options):
        try:
            data = ["Sprite", "Blue Jet", "Elve", "Halo", "Gigantic Jet", "Secondary Jet"]
            for i in data:
                if not Category.objects.filter(title__iexact=i, is_default=True).exists():
                    Category.objects.create(title=i, is_default=True)
                    print(f"{i} category created.")

        except:
            self.stdout.write('Some error occurred while creating categories.')

