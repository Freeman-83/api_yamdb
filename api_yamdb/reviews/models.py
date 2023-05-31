from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Title(models.Model):
    ...


class Review(models.Model):
    titlle = models.ForeignKey(
        Title, verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews')
    text = models.TextField(verbose_name='Текст')
    # score =
    author = models.ForeignKey(
        User, verbose_name='Автор',
        on_delete=models.CASCADE, related_name='reviews')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True)

