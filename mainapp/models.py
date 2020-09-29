from django.db import models

class BaseGame(models.Model):
    """
    Базовый класс для наследования разными играми
    """
    title = models.CharField(
        'название игры',
        max_length=20
    )
    desc = models.TextField(
        'краткое описание игры',
        max_length=1000
    )
    begin = models.DateTimeField(
        'время начала игры',
        auto_now_add=True
    )
    end = models.DateTimeField(
        'время окончания игры',
        blank=True, null=True
    )
