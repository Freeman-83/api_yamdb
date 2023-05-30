from django.db import models


class Review(models.Model):
    pass


class Category(models.Model):
    name = models.CharField('Категория', unique=True, max_length=64)
    slug = models.SlugField('URL_category', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Жанр', unique=True, max_length=64)
    slug = models.SlugField('URL_genre', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Наименование произведения', max_length=64)
    description = models.TextField('Описание')
    year = models.DateTimeField(
        'Дата выхода/публикации', auto_now_add=True, db_index=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name='titles'
    )
    genres = models.ManyToManyField(
        Genre, through='TitleGenre'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(fields=['title', 'genre'],
                                    name='unique_title_genre')
        ]

    def __str__(self):
        return f'{self.title} - {self.genre}'
