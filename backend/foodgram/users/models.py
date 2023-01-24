from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import username_validator


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        'Имя пользователя',
        max_length=100,
        unique=True,
        validators=[username_validator]
    )
    email = models.EmailField(
        'Почта',
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=50
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=50
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    def __str__(self):
        return str(self.author)
