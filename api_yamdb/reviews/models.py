from django.db import models


class Category(models.Model):
    name = models.CharField('Категория', unique=True, max_length=256)
    slug = models.SlugField('URL_category', unique=True, max_length=50)

    class Meta:
        ordering = ['slug']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.slug


class Genre(models.Model):
    name = models.CharField('Жанр', unique=True, max_length=256)
    slug = models.SlugField('URL_genre', unique=True, max_length=50)

    class Meta:
        ordering = ['slug']
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.CharField('Наименование произведения', max_length=256)
    year = models.IntegerField('Дата выхода')
    description = models.TextField('Описание', null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre, through='TitleGenre'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(fields=['title', 'genre'],
                                    name='unique_title_genre')
        ]

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    text = models.TextField()
    score = models.IntegerField()
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='review'
    )
