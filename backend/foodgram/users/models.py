from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import username_validator

# Перенести max_lenght в settings

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