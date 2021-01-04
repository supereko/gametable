# pylint: disable=invalid-str-returned)
from django.db import models


class CardType(models.Model):
    """Модель типа карты."""

    DOOR = 'door'
    TREASURE = 'treasure'
    TYPE_CHOICES = (
        (DOOR, 'Дверь'),
        (TREASURE, 'Сокровище')
    )

    name = models.CharField(
        verbose_name='наименование',
        max_length=25,
        choices=TYPE_CHOICES,
        unique=True,
    )

    def __str__(self):
        return self.get_name_display()

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'тип карты'
        verbose_name_plural = 'типы карт'


class CardSubType(models.Model):
    """Модель под-типа карты."""

    ITEM = 'item'
    LEVEL = 'level'
    OTHER = 'other'
    MONSTER = 'monster'
    WEAKNESS = 'weakness'
    MODIFFICATION = 'mod'
    KLASS = 'klass'
    RACE = 'race'

    SUBTYPE_CHOICES = (
        (ITEM, 'Шмотка'),
        (LEVEL, 'Уровень'),
        (OTHER, 'Другое'),
        (MONSTER, 'Монстр'),
        (WEAKNESS, 'Проклятие'),
        (MODIFFICATION, 'Модиффикация'),
        (KLASS, 'Класс'),
        (RACE, 'Раса'),
    )

    name = models.CharField(
        verbose_name='наименование',
        max_length=25,
        choices=SUBTYPE_CHOICES,
        unique=True,
    )
    card_type = models.ForeignKey(
        to=CardType,
        on_delete=models.PROTECT,
        verbose_name='подтип карты',
        related_name='sub_types'
    )

    def __str__(self):
        return self.get_name_display()

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'подтип карты'
        verbose_name_plural = 'подтипы карт'


class ItemType(models.Model):
    """Модель типа шмотки."""

    ONETIME = 'onetime'
    HEAD = 'head'
    ARMOR = 'armor'
    FOOT = 'foot'
    WEAPON = 'weapon'
    OTHER = 'other'

    TYPE_CHOICES = (
        (ONETIME, 'Разовая'),
        (HEAD, 'Головняк'),
        (ARMOR, 'Бронь'),
        (FOOT, 'Обувка'),
        (WEAPON, 'Оружие'),
        (OTHER, 'Другое'),
    )

    name = models.CharField(
        verbose_name='наименование',
        max_length=25,
        choices=TYPE_CHOICES,
        unique=True,
    )

    def __str__(self):
        return self.get_name_display()

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'тип шмотки'
        verbose_name_plural = 'типы шмоток'


class Item(models.Model):
    """Модель шмотки."""

    item_type = models.ForeignKey(
        to=ItemType,
        on_delete=models.PROTECT,
        verbose_name='тип шмотки',
        related_name='items',
    )
    is_large = models.BooleanField(
        verbose_name='большая',
        default=False,
    )
    damage = models.PositiveSmallIntegerField(
        verbose_name='урон шмотки',
    )
    hand_count = models.PositiveSmallIntegerField(
        verbose_name='кол-во рук'
    )

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'шмотка'
        verbose_name_plural = 'шмотки'


class Monster(models.Model):
    """Модель монстра."""

    level = models.PositiveSmallIntegerField(
        verbose_name='уровень монстра',
    )
    is_undead = models.BooleanField(
        verbose_name='нежить',
        default=False,
    )
    treasure_count = models.PositiveSmallIntegerField(
        verbose_name='кол-во сокровищ за победу',
    )
    win_levels = models.PositiveSmallIntegerField(
        verbose_name='кол-во уровней за победу',
    )

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'монстр'
        verbose_name_plural = 'монстры'


class Card(models.Model):
    """Модель карты."""

    name = models.CharField(
        verbose_name='наименование',
        max_length=50,
    )
    description = models.TextField(
        verbose_name='описание',
    )
    image = models.ImageField(
        verbose_name='изображение',
    )
    sub_type = models.ForeignKey(
        to=CardSubType,
        on_delete=models.PROTECT,
        verbose_name='подтип карты',
        related_name='cards',
    )
    monster = models.OneToOneField(
        to=Monster,
        on_delete=models.PROTECT,
        verbose_name='монстр',
        null=True, blank=True,
    )
    item = models.OneToOneField(
        to=Item,
        on_delete=models.PROTECT,
        verbose_name='шмотка',
        null=True, blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'карта'
        verbose_name_plural = 'карты'


class Effects(models.Model):
    """Модель эффектов карт."""

    card = models.ForeignKey(
        to=Card,
        on_delete=models.PROTECT,
        verbose_name='карта',
        related_name='effects',
    )
    effect = models.CharField(
        verbose_name='наименование метода эффекта',
        max_length=100,
    )

    def __str__(self):
        return self.effect

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'эффект'
        verbose_name_plural = 'эффекты'


class Game(models.Model):
    """Модель игры."""

    start_time = models.DateTimeField(
        auto_now_add=True
    )
    end_time = models.DateTimeField()

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'игра'
        verbose_name_plural = 'игры'


class Player(models.Model):
    """Модель игрока."""

    name = models.CharField(
        verbose_name='имя игрока',
        max_length=25,
    )
    level = models.PositiveSmallIntegerField(
        verbose_name='уровень игрока',
    )
    models.ForeignKey(
        to=Game,
        on_delete=models.CASCADE,
        verbose_name='игра',
        related_name='games',
    )
    on_hand = models.ForeignKey(
        to=Card,on_delete=models.SET_NULL,
        verbose_name='карты игрока на руке',
        related_name='hand_cards',
        null=True, blank=True,
    )
    on_table = models.ForeignKey(
        to=Card,on_delete=models.SET_NULL,
        verbose_name='карты игрока на столе (в игре)',
        related_name='table_cards',
        null=True, blank=True,
    )
    on_free_table = models.ForeignKey(
        to=Card, on_delete=models.SET_NULL,
        verbose_name='карты игрока на столе (но не в игре)',
        related_name='freetable_cards',
        null=True, blank=True,
    )
    weakness = models.ForeignKey(
        to=Card, on_delete=models.SET_NULL,
        verbose_name='проклятия, ослабляющие игрока',
        related_name='weakness_cards',
        null=True, blank=True,
    )

    class Meta:
        # pylint: disable=missing-docstring
        verbose_name = 'игрок'
        verbose_name_plural = 'игроки'