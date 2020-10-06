from rest_framework import serializers

from apps.mainapp.models import CardType


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
