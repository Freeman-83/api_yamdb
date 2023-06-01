# Generated by Django 3.2 on 2023-06-01 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_auto_20230601_2348'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='titlegenre',
            options={'ordering': ['title']},
        ),
        migrations.RemoveConstraint(
            model_name='titlegenre',
            name='unique_title_genre',
        ),
        migrations.RenameField(
            model_name='titlegenre',
            old_name='genre_id',
            new_name='genre',
        ),
        migrations.RenameField(
            model_name='titlegenre',
            old_name='title_id',
            new_name='title',
        ),
        migrations.AddConstraint(
            model_name='titlegenre',
            constraint=models.UniqueConstraint(fields=('title', 'genre'), name='unique_title_genre'),
        ),
    ]
