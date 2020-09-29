from django.db import models
from django.contrib.auth.models import AbstractUser

from munchkin.enums import GENDER
from munchkin.game import Game


class Gamer(AbstractUser):
    name = models.CharField(
        'Имя игрока',
        max_length=25,
        null=True, blank=False
    )
    password = models.CharField(
        'пароль',
        max_length=20
    )
    avatar = models.ImageField(
        upload_to='users_avatars',
        blank=True
    )
    gender = models.CharField(
        'Пол',
        max_length=15,
        choices=GENDER,
        blank=True, null=True
    )


class Membership(models.Model):
    gamer = models.ForeignKey(
        Gamer,
        on_delete=models.CASCADE
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )
    datetime_joined = models.DateTimeField(
        'дата и время присоединения к игре',
        auto_now_add=True
    )
