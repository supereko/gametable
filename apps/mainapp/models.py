# pylint: disable=invalid-str-returned)
import time

import rom
from django.db import models
from rom import ClassProperty
from rom import Query as mainQuery


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


class Game(rom.Model):
    """Модель игры."""

    # уникальный uid
    uid = rom.PrimaryKey()
    # время начала игры
    start_time = rom.Float(default=time.time)
    # статус игры
    # RECRUITMENT = "Набор игроков"
    # DEAL_OF_CARDS = "Раздача карт"
    # MOVE = 'Чей-то ход'
    # GAME_OVER = 'Конец игры'
    status = rom.String(
        required=True, suffix=True,
        default=b'recruitment', keygen=rom.SIMPLE,
    )
    # обратная связь для игроков
    players = rom.OneToMany('Player')

    @ClassProperty
    def query(cls):
        """Переопределяем чтоб инициализировать свойство model,
        которое нужно для получения basename при построении маршрутизации"""
        class Query(mainQuery):
            __slots__ = '_model model _filters _order_by _limit _select'.split()

            def __init__(self, model, filters=(), order_by=None, limit=None, select=None):
                self._model = self.model = model
                self._filters = filters
                self._order_by = order_by
                self._limit = limit
                self._select = select

        return Query(cls)


class Player(rom.Model):
    """Модель игрока."""

    # имя игрока
    name = rom.String(
        required=True, index=True,
        suffix=True, prefix=True,
        keygen=rom.FULL_TEXT
    )
    # уровень игрока
    level = rom.Integer(default=1)
    # ссылка на игру
    game = rom.ManyToOne('Game', on_delete='cascade')
    # ссылка на карты игрока в руке
    on_hand = rom.ForeignModel(Card)
    # ссылка на карты игрока на столе (в игре)
    on_table = rom.ForeignModel(Card)
    # ссылка на карты игрока на столе (но не в игре)
    on_free_table = rom.ForeignModel(Card)
    # ссылка на карты-проклятия, ослабляющие игрока
    weakness = rom.ForeignModel(Card)
    created_at = rom.Float(default=time.time)

    def str(self):
        return f'Манчкин {self.name} ({self.level} уровня)'

    @ClassProperty
    def query(cls):
        """Переопределяем чтоб инициализировать свойство model,
        которое нужно для получения basename при построении маршрутизации"""
        class Query(mainQuery):
            __slots__ = '_model model _filters _order_by _limit _select'.split()

            def __init__(self, model, filters=(), order_by=None, limit=None, select=None):
                self._model = self.model = model
                self._filters = filters
                self._order_by = order_by
                self._limit = limit
                self._select = select

        return Query(cls)