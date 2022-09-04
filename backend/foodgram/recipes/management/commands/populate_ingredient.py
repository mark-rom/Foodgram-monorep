import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient

BASE_DIR = settings.BASE_DIR


class Command(BaseCommand):
    help = 'populates recipes_ingredient table'
    model_name = Ingredient

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='filename for csv file')

    def get_current_app_path(self):
        return BASE_DIR / 'backend_static/data'

    def get_csv_file(self, filename):
        app_path = self.get_current_app_path()
        return app_path / filename

    def clear_model(self):
        try:
            self.model_name.objects.all().delete()
        except Exception as e:
            raise CommandError(
                f'Error in clearing {self.model_name}: {str(e)}'
            )

    def insert_to_db(self, data):
        try:
            self.model_name.objects.create(**data)
        except Exception as e:
            raise CommandError(
                f'Error in inserting {self.model_name.__name__}: {str(e)}'
            )

    def row_process(self, num, row):
        data = {}
        data['id'] = num
        data['name'] = row[0]
        data['measurement_unit'] = row[1]
        self.insert_to_db(data)

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        self.stdout.write(self.style.SUCCESS(f'filename:{filename}'))
        file_path = self.get_csv_file(filename)
        line_count = 1

        try:
            csv_file = open(file_path, encoding='utf-8')
        except FileNotFoundError:
            raise CommandError(f'File {file_path} does not exist')

        csv_reader = csv.reader(csv_file, delimiter=',')
        self.clear_model()

        for num, row in enumerate(csv_reader, start=1):

            if row != '' and line_count >= 1:
                self.row_process(num, row)

            line_count += 1

        csv_file.close()

        self.stdout.write(
            self.style.SUCCESS(
                f'{line_count} entries added to {self.model_name.__name__}'
            )
        )
