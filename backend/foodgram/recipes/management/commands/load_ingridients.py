"""
Команда для загрузки данных из csv файла. Путь к файлу задается как аргумент
команды.
"""

import csv

from django.core.management.base import BaseCommand

from ...models import Ingredient


class Command(BaseCommand):

    help = 'Загрузка данных из указанного файла'

    def add_arguments(self, parser):

        parser.add_argument(
            'file_path',
            type=str,
        )

    def handle(self, *args, **options):

        number_of_records_in_base = Ingredient.objects.count()
        reader = csv.DictReader(
                open(options['file_path']),
                fieldnames=['name', 'measurement_unit']
        )

        Ingredient.objects.bulk_create([Ingredient(**data) for data in reader])

        if (Ingredient.objects.count() > number_of_records_in_base):
            self.stdout.write(self.style.SUCCESS('Successfully loaded'))
        else:
            self.stdout.write(self.style.ERROR('NOT loaded'))
