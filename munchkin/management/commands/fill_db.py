import json
import os

from django.core.management.base import BaseCommand

from authapp.models import Gamer
from gametable.settings import BASE_DIR
from munchkin.models import CurseCard
from munchkin.models import KlassCard
from munchkin.models import KlassRelationShip
from munchkin.models import ModificatorCard
from munchkin.models import MonsterCard
from munchkin.models import OtherCard
from munchkin.models import RaceCard
from munchkin.models import RaceRelationShip
from munchkin.models import TreasuresCard


JSON_PATH = BASE_DIR + '/munchkin/json'


def load_from_json(file_name):
    with open(os.path.join(JSON_PATH, file_name + '.json'), 'r', encoding='utf-8') as infile:
        return json.load(infile)


class Command(BaseCommand):

    MonsterCard.objects.all().delete()
    TreasuresCard.objects.all().delete()
    KlassCard.objects.all().delete()
    RaceCard.objects.all().delete()
    ModificatorCard.objects.all().delete()
    CurseCard.objects.all().delete()
    KlassRelationShip.objects.all().delete()
    RaceRelationShip.objects.all().delete()
    OtherCard.objects.all().delete()

    def handle(self, *args, **options):
        monsters = load_from_json('monsters')
        [MonsterCard.objects.create(**monster) for monster in monsters]

        curses = load_from_json('curses')
        [CurseCard.objects.create(**curse) for curse in curses]

        klasses = load_from_json('klasses')
        [KlassCard.objects.create(**klass) for klass in klasses]

        modifs = load_from_json('modifs')
        [ModificatorCard.objects.create(**modif) for modif in modifs]

        races = load_from_json('races')
        [RaceCard.objects.create(**race) for race in races]
        RaceCard.objects.create(
            name="Человек",
            description="Техническая карта - не для выдачи",
            quantity_cards=5
        )

        treasures = load_from_json('treasures')
        for treasure in treasures:
            klasses = KlassCard.objects.filter(
                name__in=treasure['for_klasses_only'].replace(' ', '').split(',')
            )
            races = RaceCard.objects.filter(
                name__in=treasure['for_races_only'].replace(' ', '').split(',')
            )
            tc = TreasuresCard.objects.create(
                name=treasure['name'],
                description=treasure['description'],
                image=treasure['image'],
                is_headdress=treasure['is_headdress'],
                is_armor=treasure['is_armor'],
                is_for_hands=treasure['is_for_hands'],
                is_footwear=treasure['is_footwear'],
                bonus=treasure['bonus'],
                price_nom=treasure['price_nom'],
                is_big_size=treasure['is_big_size'],
                how_many_hands_take=treasure['how_many_hands_take'],
                is_one_time=treasure['is_one_time'],
                is_moment=treasure['is_moment']
            )
            if klasses:
                for klass in klasses:
                    klass.treasurescard_set.add(tc)
            if races:
                for race in races:
                    race.treasurescard_set.add(tc)

        others = load_from_json('othercards')
        [OtherCard.objects.create(**other) for other in others]

        klass_rels = load_from_json('klassrelationships')
        klrs = list()
        for klass_rel in klass_rels:
            try:
                klass = KlassCard.objects.get(name=klass_rel['klass'])
            except KlassCard.DoesNotExist:
                print(f"Не загружен класс {klass_rel['klass']}")
                return
            try:
                monster = MonsterCard.objects.get(name=klass_rel['monster'])
            except MonsterCard.DoesNotExist:
                print(f"Не загружен монстр {klass_rel['monster']}")
                return
            klrs.append(
                KlassRelationShip(
                    klass=klass,
                    monster=monster,
                    power_modificator=klass_rel['power_modificator'],
                    can_drive_away=klass_rel['can_drive_away'],
                    damage_modificator=klass_rel['damage_modificator'],
                    adv_treasure=klass_rel['adv_treasure'],
                )
            )
        KlassRelationShip.objects.bulk_create(klrs)

        race_rels = load_from_json('racerelationships')
        rars = list()
        for race_rel in race_rels:
            try:
                race = RaceCard.objects.get(name=race_rel['race'])
            except RaceCard.DoesNotExist:
                print(f"Не загружена раса {race_rel['race']}")
                return
            try:
                monster = MonsterCard.objects.get(name=race_rel['monster'])
            except MonsterCard.DoesNotExist:
                print(f"Не загружен монстр {race_rel['monster']}")
                return
            rars.append(
                RaceRelationShip(
                    race=race,
                    monster=monster,
                    power_modificator=race_rel['power_modificator'],
                    can_drive_away=race_rel['can_drive_away'],
                    damage_modificator=race_rel['damage_modificator'],
                    adv_treasure=race_rel['adv_treasure'],
                )
            )
        RaceRelationShip.objects.bulk_create(rars)

        # Создаем суперпользователя при помощи менеджера модели
        if not Gamer.objects.filter(username='admin').exists():
            Gamer.objects.create_superuser('admin', 'admin@gametable.local', 'admin')
