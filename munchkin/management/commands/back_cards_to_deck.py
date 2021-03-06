from django.core.management.base import BaseCommand

from authapp.models import Membership
from munchkin import enums
from munchkin.game import Game
from munchkin.models import (MonsterCard, CurseCard, ModificatorCard,
                             KlassCard, RaceCard, TreasuresCard,
                             OtherCard, Munchkin)


class Command(BaseCommand):

    def handle(self, *args, **options):
        MonsterCard.objects.all().update(status=enums.ON_DECK)
        CurseCard.objects.all().update(status=enums.ON_DECK)
        ModificatorCard.objects.all().update(status=enums.ON_DECK)
        RaceCard.objects.all().update(status=enums.ON_DECK)
        KlassCard.objects.all().update(status=enums.ON_DECK)
        OtherCard.objects.all().update(status=enums.ON_DECK)
        TreasuresCard.objects.all().update(status=enums.ON_DECK)

        Munchkin.objects.all().delete()

        game1 = Game.objects.first()
        Membership.objects.filter(game=game1).delete()
