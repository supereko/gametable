from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.api.v1.serializers import CardTypeSerializer
from apps.mainapp.models import CardType


class CardTypeView(ReadOnlyModelViewSet):
    """Эндопинт получения типов карт."""

    model = CardType
    queryset = CardType.objects
    serializer_class = CardTypeSerializer
