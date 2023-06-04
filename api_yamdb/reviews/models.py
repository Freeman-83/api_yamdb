from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLE_CHOICES = [
        (USER, "user"),
        (MODERATOR, "moderator"),
        (ADMIN, "admin"),
    ]
    email = models.EmailField(
        _('email address'),
        blank=True,
        unique=True,
        max_length=254
    )
    bio = models.TextField()
    role = models.CharField(
        max_length=9,
        choices=ROLE_CHOICES,
        default=USER
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user'
            ),
        ]

    def is_admin(self):
        if self.is_staff is True:
            self.role == "admin"

    def __str__(self):
        return self.username


class ConfirmationCode(models.Model):
    confirmation_code = models.CharField(max_length=256, unique=True)
