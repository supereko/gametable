from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.api.v1.serializers import CardSerializer
from apps.api.v1.serializers import CardSubTypeSerializer
from apps.api.v1.serializers import CardTypeSerializer
from apps.api.v1.serializers import EffectsSerializer
from apps.api.v1.serializers import GameSerializer
from apps.api.v1.serializers import ItemSerializer
from apps.api.v1.serializers import ItemTypeSerializer
from apps.api.v1.serializers import MonsterSerializer
from apps.api.v1.serializers import PlayerSerializer
from apps.mainapp.models import Card
from apps.mainapp.models import CardSubType
from apps.mainapp.models import CardType
from apps.mainapp.models import Effects
from apps.mainapp.models import Game
from apps.mainapp.models import Item
from apps.mainapp.models import ItemType
from apps.mainapp.models import Monster
from apps.mainapp.models import Player


class CardTypeView(ReadOnlyModelViewSet):
    """Эндопинт получения типов карт."""

    model = CardType
    queryset = CardType.objects
    serializer_class = CardTypeSerializer


class CardSubTypeView(ReadOnlyModelViewSet):
    """Эндопинт получения подтипов карт."""

    model = CardSubType
    queryset = CardSubType.objects
    serializer_class = CardSubTypeSerializer


class ItemTypeView(ReadOnlyModelViewSet):
    """Эндопинт получения типов шмоток."""

    model = ItemType
    queryset = ItemType.objects
    serializer_class = ItemTypeSerializer


class ItemView(ReadOnlyModelViewSet):
    """Эндопинт получения шмоток."""

    model = Item
    queryset = Item.objects
    serializer_class = ItemSerializer


class MonsterView(ReadOnlyModelViewSet):
    """Эндопинт получения монстров."""

    model = Monster
    queryset = Monster.objects
    serializer_class = MonsterSerializer


class CardView(ReadOnlyModelViewSet):
    """Эндопинт получения карт."""

    model = Card
    queryset = Card.objects
    serializer_class = CardSerializer


class EffectsView(ReadOnlyModelViewSet):
    """Эндопинт получения эффектов."""

    model = Effects
    queryset = Effects.objects
    serializer_class = EffectsSerializer


class GameView(ModelViewSet):
    """Эндопинт игры (начало новой, получение списка, завершение)."""

    model = Game
    queryset = Game.query
    serializer_class = GameSerializer


class PlayerView(ModelViewSet):
    """Эндопинт игрока."""

    model = Player
    queryset = Player.query
    serializer_class = PlayerSerializer