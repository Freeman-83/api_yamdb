import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User


DATABASE = {
    Category: 'category.csv',
    Comment: 'comments.csv',
    Genre: 'genre.csv',
    Title.genre.through: 'genre_title.csv',
    Review: 'review.csv',
    Title: 'titles.csv',
    User: 'users.csv'
}


class Command(BaseCommand):
    help = 'Loading csv_files to DataBase'

    def handle(self, *args, **kwargs):
        for model, csv_file in DATABASE.items():
            if model.objects.exists():
                print('DataBase is already exist')
                return

            with open(
                    f'{settings.BASE_DIR}/static/data/{csv_file}',
                    'r',
                    encoding='utf-8',
            ) as file:
                reader = csv.DictReader(file)
                for data in reader:
                    model.objects.get_or_create(**data)
        self.stdout.write(self.style.SUCCESS('Successfully loaded data'))
