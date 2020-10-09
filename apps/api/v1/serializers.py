from rest_framework import serializers

from apps.mainapp.models import Card
from apps.mainapp.models import CardSubType
from apps.mainapp.models import CardType
from apps.mainapp.models import Effects
from apps.mainapp.models import Item
from apps.mainapp.models import ItemType
from apps.mainapp.models import Monster


class CardTypeSerializer(serializers.ModelSerializer):
    """Сериализатор типа карты."""

    name = serializers.SerializerMethodField('get_name')

    @staticmethod
    def get_name(instance: CardType):
        """Метод возращающий человекочитаемый вид имени типа карты."""
        return instance.get_name_display()

    class Meta:
        # pylint: disable=missing-class-docstring
        model = CardType
        fields = '__all__'


class CardSubTypeSerializer(serializers.ModelSerializer):
    """Сериализатор подтипа карты."""

    card_type = CardTypeSerializer()
    name = serializers.SerializerMethodField('get_name')

    @staticmethod
    def get_name(instance: CardType):
        """Метод возращающий человекочитаемый вид имени подтипа карты."""
        return instance.get_name_display()

    class Meta:
        # pylint: disable=missing-class-docstring
        model = CardSubType
        fields = '__all__'


class ItemTypeSerializer(serializers.ModelSerializer):
    """Сериализатор типа шмотки."""

    name = serializers.SerializerMethodField('get_name')

    @staticmethod
    def get_name(instance: CardType):
        """Метод возращающий человекочитаемый вид имени типа шмотки."""
        return instance.get_name_display()

    class Meta:
        # pylint: disable=missing-class-docstring
        model = ItemType
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    """Сериализатор карты шмотки."""

    item_type = ItemTypeSerializer()

    class Meta:
        # pylint: disable=missing-class-docstring
        model = Item
        fields = '__all__'


class MonsterSerializer(serializers.ModelSerializer):
    """Сериализатор карты монстра."""

    class Meta:
        # pylint: disable=missing-class-docstring
        model = Monster
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    """Сериализатор карты."""

    sub_type = CardSubTypeSerializer()
    monster = MonsterSerializer(
        allow_null=True,
        required=False
    )
    item = ItemSerializer(
        allow_null=True,
        required=False
    )

    class Meta:
        # pylint: disable=missing-class-docstring
        model = Card
        fields = '__all__'


class EffectsSerializer(serializers.ModelSerializer):
    """Сериализатор эффектов."""

    class Meta:
        # pylint: disable=missing-class-docstring
        model = Effects
        fields = '__all__'
