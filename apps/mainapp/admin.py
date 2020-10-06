from django.contrib import admin

from apps.mainapp.models import Card
from apps.mainapp.models import CardSubType
from apps.mainapp.models import CardType
from apps.mainapp.models import Effects
from apps.mainapp.models import Item
from apps.mainapp.models import ItemType
from apps.mainapp.models import Monster


@admin.decorators.register(CardType)
class CardTypeAdmin(admin.ModelAdmin):
    """Админка типов карт."""


@admin.decorators.register(CardSubType)
class CardSubTypeAdmin(admin.ModelAdmin):
    """Админка подтипов карт."""


@admin.decorators.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    """Админка типов шмоток."""


@admin.decorators.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Админка шмоток."""


@admin.decorators.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    """Админка монстров."""


@admin.decorators.register(Card)
class CardAdmin(admin.ModelAdmin):
    """Админка карт."""


@admin.decorators.register(Effects)
class EffectsAdmin(admin.ModelAdmin):
    """Админка эффектов."""
