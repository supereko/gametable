from authapp.models import Gamer
from django.test import TestCase
from munchkin.game import Game
from munchkin.management.commands.fill_db import Command
from munchkin.models import *


class TestMunchkin(TestCase):

    def setUp(self):
        # создаём игру и пользователей
        game = Game.objects.create(
            title='Манчкин',
            desc='Манчкин классический'
        )
        gosha = Gamer.objects.create(
            name='gosha',
            username='gosha',
            password='pass',
            avatar='img/gosha.jpg',
            gender=enums.MALE
        )
        masha = Gamer.objects.create(
            name='masha',
            username='masha',
            password='pass',
            avatar='img/masha.jpg',
            gender=enums.FEMALE
        )
        vasya = Gamer.objects.create(
            name='vasya',
            username='vasya',
            password='pass',
            avatar='img/vasya.jpg',
            gender=enums.MALE
        )
        gosha = Munchkin.objects.create(
            gamer=gosha,
            game=game
        )
        masha = Munchkin.objects.create(
            gamer=masha,
            game=game
        )
        vasya = Munchkin.objects.create(
            gamer=vasya,
            game=game
        )
        # загружаем карты
        Command().handle()

        # раздаём карты Гоше
        curse = CurseCard.objects.get(name='Абропокалипсис')
        klass = KlassCard.objects.get(name='Вор')
        monster = MonsterCard.objects.get(name='3872 Орка')
        modif = ModificatorCard.objects.get(name='Ядированный')

        treasure1 = TreasuresCard.objects.get(name='Хотельное кольцо')
        treasure2 = TreasuresCard.objects.get(name='Зелье пламенной отравы')
        treasure3 = TreasuresCard.objects.get(name='Плащ замутненности')
        treasure4 = TreasuresCard.objects.get(name='Бандана сволочизма')

        gosha.cursecard_set.add(curse)
        gosha.klasscard_set.add(klass)
        gosha.monstercard_set.add(monster)
        gosha.modificatorcard_set.add(modif)
        gosha.treasurescard_set.set([treasure1, treasure2, treasure3, treasure4])

        for card in [curse, monster, modif, treasure1, treasure2, treasure3, treasure4]:
            card.status = enums.ON_HAND
            card.save()
        klass.status = enums.ON_GAME
        klass.save()

    def test_level(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        self.assertEqual(gosha.set_level(5), 5)
        self.assertEqual(gosha.level_up(2), 7)
        self.assertEqual(gosha.level_up(4), 9)
        self.assertEqual(gosha.level_down(2), 7)
        self.assertEqual(gosha.level_down(8), 1)
        self.assertEqual(gosha.level_up(9, win=True), 10)

    def test_others(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        masha = Munchkin.objects.get(gamer__name='masha')
        vasya = Munchkin.objects.get(gamer__name='vasya')
        self.assertEqual(gosha.others(assistant=vasya).get(), masha)

    def test_select_assistants_other_gender(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        masha = gosha.select_assistants_other_gender().get()
        self.assertEqual(masha.gamer.gender, enums.FEMALE)

    def test_races(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        race = RaceCard.objects.get(name='Человек')
        self.assertEqual(gosha.races().get(), race)

    def test_klasses(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        klass = KlassCard.objects.get(name='Вор')
        self.assertEqual(gosha.klasses().get(), klass)

    def test_power(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # выкладываем бандану в игру
        bandana = gosha.treasurescard_set.get(name='Бандана сволочизма')
        bandana.status = enums.ON_GAME
        bandana.save()
        # надеваем Плащ замутненности
        cloak = gosha.treasurescard_set.get(name='Плащ замутненности')
        cloak.status = enums.ON_GAME
        cloak.save()
        # +3 к первому уровню, как носителю банданы сволочизма
        # +4 как Вору в плаще замутненности
        self.assertEqual(gosha.power, 8)

    def test_have_monsters(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # у Гоши в руке 3872 Орка
        self.assertEqual(gosha.have_monsters(), True)

    def test_get_treas_card(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # скидываем все сокровища для чистоты эксперимента
        for card in gosha.treasurescard_set.all():
            gosha.discard(card)
        # Скидываем в сброс 18 из 24 карт сокровищ
        cards_query = TreasuresCard.objects.filter(price_nom__gte=200)
        cards_query.update(status=enums.ON_TREAS_DISCARD)
        # в колоде остаётся 6 карт, пытаемся получить 7 карт, чтоб
        # наверняка перетасовать колоду сброса
        gosha.get_treas_card(7)
        # У Гоши теперь должно быть 7 карт сокровищ
        self.assertEqual(gosha.treasurescard_set.count(), 7)

    def test_get_doors_card(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # скидываем все карты дверей для чистоты эксперимента
        for card in chain(gosha.klasscard_set.all(),
                          gosha.cursecard_set.all(),
                          gosha.monstercard_set.all()):
            gosha.discard(card)
        # Скидываем в сброс 42 из 50 карт дверей
        klass_cards = KlassCard.objects.exclude(name='Воин')
        klass_cards.update(status=enums.ON_DOORS_DISCARD)
        race_cards = RaceCard.objects.exclude(name='Гном')
        race_cards.update(status=enums.ON_DOORS_DISCARD)
        curse_cards = CurseCard.objects.exclude(name='Абропокалипсис')
        curse_cards.update(status=enums.ON_DOORS_DISCARD)
        other_cards = OtherCard.objects.exclude(name='Полукровка')
        other_cards.update(status=enums.ON_DOORS_DISCARD)
        modif_cards = ModificatorCard.objects.exclude(name='Благословенный')
        modif_cards.update(status=enums.ON_DOORS_DISCARD)
        monster_cards = MonsterCard.objects.filter(level__gte=3)
        monster_cards.update(status=enums.ON_DOORS_DISCARD)
        # в колоде остаётся 8 карт, пытаемся получить 9 карт, чтоб
        # наверняка перетасовать колоду сброса
        gosha.get_doors_card(9)

    def test_place_in_hands(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # после раздачи карт в руке Гоши 7 карт - это много
        # (карту класса сразу выложили в игру)
        self.assertEqual(gosha.place_in_hands(), False)
        # скидываем ещё парочку карт
        monster = gosha.monstercard_set.first()
        modif = gosha.modificatorcard_set.first()
        gosha.discard(monster)
        gosha.discard(modif)
        # теперь карт должно быть нормальное количество
        self.assertEqual(gosha.place_in_hands(), True)

    def test_place_on_head(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # сейчас у Гоши из шмоток, занимающих слоты с оружием,
        # только бандана сволочизма на голове
        helm = TreasuresCard.objects.get(name='Шлем отваги')
        # пробуем надеть шлем на бандану, не должно получиться
        self.assertEqual(gosha.place_on_head(), False)
        # снимаем бандану
        gosha.discard(gosha.treasurescard_set.get(name='Бандана сволочизма'))
        # а теперь должно
        self.assertEqual(gosha.place_on_head(), True)

    def test_place_for_armor(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # проверяем, можно ли надеть бронник, должно получиться
        self.assertEqual(gosha.place_for_armor(), True)
        # надеваем
        armor = TreasuresCard.objects.get(name='Слизистая оболочка')
        gosha.treasurescard_set.add(armor)
        armor.status = enums.ON_GAME
        # теперь места не должно быть
        self.assertEqual(gosha.place_for_armor(), False)

    def test_place_on_foot(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # проверяем, можно ли надеть что-то на ноги, должно получиться
        self.assertEqual(gosha.place_on_foot(), True)
        # надеваем Башмаки могучего пенделя
        footwear = TreasuresCard.objects.get(name='Башмаки могучего пенделя')
        gosha.treasurescard_set.add(footwear)
        footwear.status = enums.ON_GAME
        # теперь места новой обувки не должно быть
        self.assertEqual(gosha.place_on_foot(), False)

    def test_place_on_hands(self):
        gosha = Munchkin.objects.get(gamer__name='gosha')
        # в руках у Гоши пусто, можно взять что угодно
        bow = TreasuresCard.objects.get(name='Лучок с ленточками')
        # проверяем есть ли место для лучка в руках
        self.assertEqual(gosha.place_on_hands(bow), True)
        # берем лучок, при этом руки должны закончиться
        gosha.treasurescard_set.add(bow)
        bow.status = enums.ON_GAME
        self.assertEqual(gosha.place_on_hands(bow), False)

