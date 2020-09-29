import datetime
import random
from itertools import chain

from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.db import models

from munchkin import enums


def dice_roll():
    """
    Функция кидания 6-тигранного кубика
    """
    return random.randint(1, 6)


class Munchkin(models.Model):
    """
    Манчкин
    """
    gamer = models.OneToOneField(
        'authapp.Gamer',
        on_delete=models.CASCADE
    )
    game = models.ForeignKey(
        'Game',
        on_delete=models.CASCADE
    )
    level = models.PositiveSmallIntegerField(
        'Уровень манчкина',
        default=1,
        validators=[MinValueValidator(1)]
    )
    is_next_move = models.BooleanField(
        'Его ход следущий',
        default=False
    )
    next = models.ForeignKey(
        'self',
        blank=True, null=True,
        default=None,
        on_delete=models.SET_NULL
    )
    is_want_to_continue = models.BooleanField(
        'Хочет продолжать участие в подкидывании карт бьющемуся манчкину',
        default=True
    )
    discard_count = models.SmallIntegerField(
        'Количество карт, которые может сбросить манчкин '
        'для усиления себя во время каждого боя',
        default=0,
        validators=[MinValueValidator(3)]
    )
    undercut_count = models.SmallIntegerField(
        'Количество раз, которое манчкин с классом Вор'
        'может подрезать одного игрока в бою',
        default=0,
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f'Манчкин {self.gamer.name} {self.level} уровня ' \
               f'{"".join([klass.name for klass in self.klasses()])} ' \
               f'{"".join([race.name for race in self.races()])} ' \
               f'сила {self.power}'

    @property
    def power(self):
        """
        Функция для определения силы Манчкина путем сложения
        уровня, действующих (лежащих на столе) карт головняка, брони и
        оружия в руках, с учётом преимуществ/недостатков расы,
        класса и действующих проклятий без учета сыгранных в момент боя карт
        """
        bonus_cards = self.treasurescard_set.filter(
            is_one_time=False,
            status=enums.ON_GAME,
        )
        bonus_power = 0
        if bonus_cards.exists():
            for card in bonus_cards:
                if card.for_races_only_id in self.races().values_list('id', flat=True) or \
                    card.for_klasses_only_id in self.klasses().values_list('id', flat=True) or \
                    card.for_races_only == card.for_klasses_only == None:
                    bonus_power += card.bonus
        return self.level + bonus_power

    def level_up(self, n, win=False):
        """
        Функция для повышения уровня манчкина на n единиц
        параметр win используется в случаях победы над монстром
        либо божественного вмешательства
        """
        if win:
            self.level += n
            if self.level > 9:
                game = 'Название игры'
                # TODO Сделать исключение на этот случай
                print(f"Победа игрока {self} в игре {game}")
        else:
            self.level += n
            if self.level > 9:
                # победить можно только убив монстра или
                # благодаря божественному вмешательству
                self.level = 9
        return self.level

    def level_down(self, n):
        """
        Функция для уменьшения уровня манчкина на n единиц
        """
        self.level -= n
        if self.level < 1:
            self.level = 1
        return self.level

    def set_level(self, n):
        """
        Функция для установки уровня манчкина в n
        """
        self.level = n
        return self.level

    def have_monsters(self):
        """
        Функция проверки можно ли сыграть монстра с руки
        """
        return self.monstercard_set.exists()

    def get_doors_card(self, count):
        """
        Функция для получения count карт двери из колоды дверей
        """
        all_doors_cards_in_deck = list()
        for card in [KlassCard,
                     MonsterCard,
                     CurseCard,
                     ModificatorCard,
                     OtherCard]:
            all_doors_cards_in_deck.extend(
                card.objects.filter(status=enums.ON_DECK)
            )
        all_doors_cards_in_deck.extend(
            RaceCard.objects.filter(status=enums.ON_DECK
                                    ).exclude(name='Человек')
        )
        if len(all_doors_cards_in_deck) >= count:
            card_for_issue = list()
            for card in random.sample(all_doors_cards_in_deck, count):
                if isinstance(card, KlassCard):
                    self.klasscard_set.add(card)
                elif isinstance(card, RaceCard):
                    self.racecard_set.add(card)
                elif isinstance(card, MonsterCard):
                    self.monstercard_set.add(card)
                elif isinstance(card, OtherCard):
                    self.othercard_set.add(card)
                elif isinstance(card, ModificatorCard):
                    self.modificatorcard_set.add(card)
                card.status = enums.ON_HAND
                card.save()
                card_for_issue.append(card)
            print(f'Карты для выдачи {card_for_issue}')
            return card_for_issue
        # если колода дверей закончилась, переворачиваем, тасуем и снова из неё берем
        else:
            print('Перетасовываем сброс колоды дверей')
            all_doors_cards_in_discard = list()
            for card in [KlassCard,
                         MonsterCard,
                         CurseCard,
                         ModificatorCard,
                         OtherCard,
                         RaceCard]:
                all_doors_cards_in_discard.extend(
                    card.objects.filter(status=enums.ON_DOORS_DISCARD)
                )
            if len(all_doors_cards_in_discard) + len(all_doors_cards_in_deck) < count:
                print('Не осталось карт для выдачи игрокам')
                pass
            else:
                for card in all_doors_cards_in_discard:
                    card.status=enums.ON_DECK
                    card.save()
            return self.get_doors_card(count)

    def get_treas_card(self, count):
        """
        Функция для получения count карт сокровищ из колоды
        """
        all_treasures_in_deck = TreasuresCard.objects.filter(
            status=enums.ON_DECK
        )
        if all_treasures_in_deck.count() >= count:
            card_list = random.sample(list(all_treasures_in_deck), count)
            self.treasurescard_set.set(card_list)
            for card in card_list:
                card.status=enums.ON_HAND
                card.save()
            return card_list
        else:
            all_treasures_in_discard = TreasuresCard.objects.filter(
                status=enums.ON_TREAS_DISCARD
            )
            if all_treasures_in_discard.count() + all_treasures_in_deck.count() < count:
                print('Не осталось карт для выдачи игрокам')
                return
            print('Перетасовываем сброс колоды сокровищ')
            all_treasures_in_discard.update(status=enums.ON_DECK)
            self.get_treas_card(count)

    def doors_card_in_hand(self):
        """
        Функция, возвращающая набор карт дверей в руке манчкина
        """
        curse_cards = CurseCard.objects.filter(
            status=enums.ON_HAND,
            munchkin=self
        )
        monster_cards = MonsterCard.objects.filter(
            status=enums.ON_HAND,
            munchkin=self
        )
        modif_cards = ModificatorCard.objects.filter(
            status=enums.ON_HAND,
            munchkin=self
        )
        klass_cards = KlassCard.objects.filter(
            status=enums.ON_HAND,
            munchkin=self
        )
        race_cards = RaceCard.objects.filter(
            status=enums.ON_HAND,
            munchkin=self
        )
        return chain(curse_cards, monster_cards, modif_cards, klass_cards, race_cards)

    def treasures_card_in_hand(self):
        """
        Функция, возвращающая набор карт сокровищ в руке манчкина
        """
        return self.treasurescard_set.filter(status=enums.ON_HAND)

    def all_card_in_hand(self):
        """
        Функция возвращающая все карты в руке манчкина
        TODO возможно стоит заменить chain на список
        """
        return chain(
            self.doors_card_in_hand(),
            self.treasures_card_in_hand()
        )

    def place_in_hands(self):
        """
        Функция для проверки есть ли место в руках,
        которыми игрок держит карты
        в случае когда в руке игрока карт больше чем положено
        возвращает False
        """
        how_much_cards = len(list(self.doors_card_in_hand())) + \
                         self.treasures_card_in_hand().count()
        how_allowed = enums.MAX_ALLOWED_CARD
        if "Дварф" in [race for race in self.races()]:
            how_allowed = 6
        return how_much_cards <= how_allowed

    def place_on_hands(self, new_thing):
        """
        Функция для того, чтобы понять свободны ли руки игрока,
        возвращает да/нет, учитывая условия расы, наёмничка, уже
        занятые слоты и что мы хотим взять в руки new_thing
        """
        all_place_in_hands = 2
        if 'Дварф' in self.races():
            return True
        # смотрим, сколько рук занято
        hands_place = self.treasurescard_set.filter(
            is_for_hands=True,
            is_one_time=False,
        )
        if hands_place.exists():
            hands_place = hands_place.aggregate(
            total=Sum('how_many_hands_take')
            )['total']
        else:
            hands_place = 0
        hireling = self.treasurescard_set.filter(
            name='Наёмничек',
            status=enums.ON_GAME
        ).exists()
        if hireling:
            all_place_in_hands += 2
        return new_thing.how_many_hands_take <= all_place_in_hands - hands_place

    def place_on_head(self):
        """
        Функция для того, чтобы понять можно ли надеть на голову
        новый головняк
        Если другого головняка не надето, то есть
        """
        head_place = self.treasurescard_set.filter(
            is_headdress=True
        ).exists()
        return head_place is False

    def place_for_armor(self):
        """
        Функция для того, чтобы понять можно ли надеть
        новый бронник
        Если другого бронника не надето, то можно
        """
        armor_place = self.treasurescard_set.filter(
            is_armor=True
        ).exists()
        return armor_place is False

    def place_on_foot(self):
        """
        Функция для того, чтобы понять можно ли надеть новую
        обувку
        Если другая обувка не надета, то можно
        """
        boots_place = self.treasurescard_set.filter(
            is_footwear=True
        ).exists()
        return boots_place is False

    def wear_thing(self, new_thing):
        """
        Функция для надевания шмотки на манчкина
        new_thing - TreasuresCard
        """
        if any(
                [
                    new_thing.is_armor and self.place_for_armor(),
                    new_thing.is_headdress and self.place_on_head(),
                    new_thing.is_for_hands and self.place_on_hands(new_thing),
                    new_thing.is_footwear and self.place_on_foot()
                ]
        ):
            self.treasurescard_set.add(new_thing)
            new_thing.status = enums.ON_GAME
            new_thing.save()
        print(f'Для шмотки {new_thing} нет места на манчкине {self}')

    def select_assistants_other_gender(self):
        """
        Функция возвращает список манчкинов другого пола
        """
        other_gender = enums.MALE if self.gamer.gender == enums.FEMALE \
            else enums.FEMALE
        return Munchkin.objects.filter(
            game=self.game,
            gamer__gender=other_gender
        )

    def others(self, assistant=None):
        """
        Функция возвращает остальных манчкинов игры, не участвующих в битве
        """
        exclude_ids = [self.id]
        if assistant:
            exclude_ids.append(assistant.id)
        return Munchkin.objects.exclude(id__in=exclude_ids)

    def is_super(self):
        """
        Функция возвращает True если это суперманчкин
        """
        return self.treasurescard_set.filter(
            name='Суперманчкин',
            status=enums.ON_GAME
        ).exists()

    def is_halfbreed(self):
        """
        Функция возвращает True если это полукровка
        """
        return self.treasurescard_set.filter(
            name='Полукровка',
            status=enums.ON_GAME
        ).exists()

    def klasses(self):
        """
        Функция возвращает все задействованные классы манчкина
        """
        return self.klasscard_set.filter(
            status=enums.ON_GAME)

    def races(self):
        """
        Функция возвращает все задействованные расы манчкина
        """
        races = self.racecard_set.filter(
            status=enums.ON_GAME
        )
        if not races:
            races = RaceCard.objects.filter(name='Человек')
        return races

    def loose_klasses(self):
        """
        Функция для потери всех классов манчкина
        """
        self.klasscard_set.update(status=enums.ON_DECK)
        self.klasscard_set.remove()

    def loose_races(self):
        """
        Функция для потери всех рас манчкина
        """
        self.racecard_set.update(status=enums.ON_DECK)
        self.racecard_set.remove()

    def from_hand_on_game(self, card):
        """
        Функция для попытки ввести карту с руки в игру
        """
        if isinstance(card, KlassCard) and \
                (self.klasses().count() < 2 and self.is_super() or self.klasses().count() < 1):
            self.klasscard_set.add(card)
            card.status = enums.ON_GAME
        elif isinstance(card, RaceCard) and \
                (self.races().count() < 2 and self.is_halfbreed() or
                 self.races().exclude(name='Человек').count() < 1):
            self.racecard_set.add(card)
            card.status = enums.ON_GAME
        elif isinstance(card, TreasuresCard) and card.is_one_time == False:
            self.wear_thing(card)
        elif isinstance(card, TreasuresCard) and card.is_one_time == True:
            card.status = enums.ON_GAME
        else:
            print(f'Карту {card} нельзя ввести в игру')
        card.save()


    def curse_run(self, curse_card):
        """
        Функция для приёма/отбивания проклятия
        """
        # проверяем, есть ли карты отбивающие проклятие
        escape_curse_card = self.treasurescard_set.filter(
            name__in=['Хотельное кольцо', 'Шипованные сапоги'],
            status=enums.ON_GAME
        )
        if escape_curse_card.exists():
            # Игрок выбирает отбить ли проклятие и чем отбить, если да
            protect_card = escape_curse_card.first()
            input = random.choice([False, protect_card])
            # если отбил картой защищающей разово, скидывает её в сброс
            if input:
                protect_card.status = enums.ON_DOORS_DISCARD
                # TODO возможно время само проставится, надо проверить
                protect_card.touched = datetime.datetime.now()
                if protect_card.is_one_time:
                    self.treasurescard_set.remove(protect_card)
        # если не отбиваем разово действующее проклятие
        elif curse_card.is_one_time == True:
            # и оно потеряй уровень
            if curse_card.lose_level_count:
                self.level_down(curse_card.lose_level_count)
            # или потеряй все шмотки
            elif curse_card.lose_all_staffs:
                self.treasurescard_set.filter(
                    game=self.game,
                    status=enums.ON_GAME
                ).remove()
        # если не отбиваем длительно действующее проклятие
        # забираем его себе и кладём на стол
        else:
            self.cursecard_set.add(curse_card)
            curse_card.status = enums.ON_GAME
            curse_card.save()

    def take_card(self, card):
        """
        Функция для забирания карт в руку
        """
        if isinstance(card, MonsterCard):
            self.monstercard_set.add(card)
        elif isinstance(card, OtherCard):
            self.othercard_set.add(card)
        elif isinstance(card, KlassCard):
            self.klasscard_set.add(card)
        elif isinstance(card, RaceCard):
            self.racecard_set.add(card)
        elif isinstance(card, ModificatorCard):
            self.modificatorcard_set.add(card)
        elif isinstance(card, CurseCard):
            self.cursecard_set.add(card)
        else:
            print('Этой функцией нельзя брать сокровища, она только для карт-дверей')
            return
        card.status=enums.ON_HAND
        card.save()

    def discard(self, card):
        """
        Функция для того чтобы сбросить карту в сброс
        card - карта, которую
        """
        if isinstance(card, TreasuresCard):
            card.status = enums.ON_TREAS_DISCARD
            self.treasurescard_set.remove(card)
        elif isinstance(card, MonsterCard):
            self.monstercard_set.remove(card)
            card.status = enums.ON_DOORS_DISCARD
        elif isinstance(card, OtherCard):
            self.othercard_set.remove(card)
            card.status = enums.ON_DOORS_DISCARD
        elif isinstance(card, KlassCard):
            self.klasscard_set.remove(card)
            card.status = enums.ON_DOORS_DISCARD
        elif isinstance(card, RaceCard):
            self.racecard_set.remove(card)
            card.status = enums.ON_DOORS_DISCARD
        elif isinstance(card, ModificatorCard):
            self.modificatorcard_set.remove(card)
            card.status = enums.ON_DOORS_DISCARD
        elif isinstance(card, CurseCard):
            self.cursecard_set.remove(card)
            card.status = enums.ON_DOORS_DISCARD
        card.save()


    def set_curse(self, victim):
        """
        Функция наложения проклятия
        """

    def give_card(self, card, other_munchkin):
        """
        Функция для того, отдать карту с руки или из игры
         конкретному игроку
        """
        if isinstance(card, MonsterCard):
            self.monstercard_set.remove(card)
            other_munchkin.monstercard_set.add(card)
        elif isinstance(card, OtherCard):
            self.othercard_set.remove(card)
            other_munchkin.othercard_set.add(card)
        elif isinstance(card, KlassCard):
            self.klasscard_set.remove(card)
            other_munchkin.klasscard_set.add(card)
        elif isinstance(card, RaceCard):
            self.racecard_set.remove(card)
            other_munchkin.racecard_set.add(card)
        elif isinstance(card, ModificatorCard):
            self.modificatorcard_set.remove(card)
            other_munchkin.modificatorcard_set.add(card)
        elif isinstance(card, CurseCard):
            self.cursecard_set.remove(card)
            other_munchkin.cursecard_set.add(card)
        elif isinstance(card, TreasuresCard):
            self.treasurescard_set.remove(card)
            other_munchkin.treasurescard_set.add(card)
        else:
            print(f'Неизвестный тип карты {type(card)}')
            return


    def lost_all_hand(self):
        """
        Функция сбрасывает всю руку манчкина
        """
        for card in self.all_card_in_hand():
            self.discard(card)

    def deading(self):
        """
        Функция для потери манчкином всех карт и уровней
        """
        self.lost_all_hand()
        self.set_level(1)

    def try_to_throw_monster(self):
        """
        Функция для попытки подкинуть монстра в бою дерущемуся манчкину,
        возвращет либо монстра либо None
        """
        new_monster = None
        wandering_beasts = self.othercard_set.filter(name='Бродячая тварь')
        monsters = self.monstercard_set.all()
        # Если у манчкина есть монстр, бродячая тварь и он желает её подкинуть
        if all([
            wandering_beasts.exists(),
            monsters.exists(),
            random.choice([True, False])
        ]):
            # выбирает монстра
            new_monster = random.choice(monsters)
            wandering_beast = wandering_beasts.first()
            # скидывает тварь в сброс
            self.othercard_set.remove(wandering_beast)
            wandering_beast.status = enums.ON_DOORS_DISCARD
        return new_monster

    def try_to_throw_modif(self):
        """
        Функция для попытки подкинуть модификатор монстра в бою,
        возвращет либо модификатор либо None
        """
        new_modif = None
        modifs = self.modificatorcard_set.all()
        if modifs.exists() and random.choice([True, False]):
            new_modif = random.choice(modifs)
        return new_modif

    def try_to_self_modif(self):
        """
        Функция для попытки модифицировать себя в бою,
        возвращет либо модификатор либо None
        """
        new_modif = None
        modifs = self.modificatorcard_set.filter(
            is_monster_only=False
        )
        things = self.treasurescard_set.filter(
            is_moment='in_fight'
        )
        if modifs.exists() and random.choice([True, False]):
            new_modif = random.choice(chain(modifs, things))
            new_modif.status = enums.ON_FIGHT
            new_modif.save()
        return new_modif

    def is_want_to_continue_fight(self):
        is_want = random.choice([True, False])
        if is_want:
            self.is_want_to_continue = True
        else:
            self.is_want_to_continue = False
        self.save()

    def sell_out(self):
        """
        Функция для того, чтобы манчкин мог продать одну или больше шмоток
        Нормально будет работать после того как уигорока появится интерфейс,
        а с ним и возможность выбирать что ему продавать
        """
        if self.treasurescard_set.count() > 0:
            thing = random.choice(self.treasurescard_set.all())
            self.discard(thing)
            if 'Хафлинг' in self.races():
                gold = thing.price_nom * 2
            else:
                gold = thing.price_nom
            if gold >= 1000:
                self.level_up(1)


class Card(models.Model):
    """
    Карта любой колоды
    """
    name = models.CharField('название', max_length=100)
    description = models.TextField('описание', max_length=500)
    image = models.ImageField('изображение карты')
    munchkin = models.ForeignKey(
        'Munchkin',
        blank=True, null=True,
        on_delete=models.SET_NULL,
    )
    # нужно для прочёсывания сбросов
    touched = models.DateTimeField(
        'Время последней операции с картой',
        auto_now=True
    )
    status = models.CharField(
        'Где находится карта',
        max_length=40,
        choices=enums.CARD_STATUS,
        default=enums.ON_DECK
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RaceCard(Card):
    """
    Раса манчкина
    """
    quantity_cards = models.SmallIntegerField(
        'количество карт, которое может находиться в руке игрока в конце хода')


class KlassCard(Card):
    """
    Класс манчкина
    """


class ModificatorCard(Card):
    """
    Карта с модификатором монстра или бонуса
    """
    bonus = models.SmallIntegerField(
        'размер бонуса модификатора',
        default=0
    )
    treasure_bonus = models.SmallIntegerField(
        'кол-во дополнительных сокровищ за модифицированного монстра',
        default=0
    )
    is_monster_only = models.BooleanField(
        'модификатор монстра',
        default=False
    )


class CurseCard(Card):
    """
    Карта с проклятьем
    """
    lose_level_count = models.PositiveSmallIntegerField(
        'сколько уровней теряет манчкин',
        default=0
    )
    lose_all_staffs = models.BooleanField(
        'потеряй все шмотки',
        default=False
    )
    is_one_time = models.BooleanField(
        'разовое проклятие',
        default=True
    )

class OtherCard(Card):
    """
    Модель для остальных карт (Божественного вмешательства, Бродячих тварей и пр.)
    """

class KlassRelationShip(models.Model):
    """
    Промежуточная модель для хранения отношений Монстра с классом манчкина
    """
    klass = models.ForeignKey('KlassCard', on_delete=models.CASCADE)
    monster = models.ForeignKey('MonsterCard', on_delete=models.CASCADE)
    power_modificator = models.SmallIntegerField(
        'Модификатор силы монстра в зависимости от класса манчкина')
    can_drive_away = models.BooleanField(
        'Может просто прогнать монстра', default=False)
    damage_modificator = models.SmallIntegerField(
        'Сколько уровней теряет манчкин при поражении в зависимости от класса')
    # при победе над монстром
    adv_treasure = models.SmallIntegerField(
        'Манчкин в зависимости от класса тянет дополнительные сокровища',
        default=0
    )


class RaceRelationShip(models.Model):
    """
    Промежуточная модель для хранения отношений Монстра с расой манчкина
    """
    race = models.ForeignKey('RaceCard', on_delete=models.CASCADE)
    monster = models.ForeignKey('MonsterCard', on_delete=models.CASCADE)
    power_modificator = models.SmallIntegerField(
        'Модификатор силы монстра в зависимости от расы манчкина')
    can_drive_away = models.BooleanField(
        'Может просто прогнать монстра')
    damage_modificator = models.SmallIntegerField(
        'Сколько уровней теряет манчкин при поражении в зависимости от расы')
    # при победе монстра
    adv_treasure = models.SmallIntegerField(
        'Манчкин в зависимости от расы тянет дополнительные сокровища', default=0)


class MonsterCard(Card):
    """
    Карта с монстром
    """
    level = models.SmallIntegerField('уровень монстра')
    is_undead = models.BooleanField('Монстер - андед?', default=False)
    treasure_count = models.SmallIntegerField(
        'кол-во сокровищ, которое дают за победу в бою с этим монстром')
    damage_desc = models.CharField('описание непотребства при смывке', max_length=300)
    level_down_nom = models.PositiveSmallIntegerField(
        'номинальное кол-во уровней, которое теряет проигравший монстру манчкин',
        default=1
    )
    level_up_nom = models.PositiveSmallIntegerField(
        'номинальное кол-во уровней, которое даёт побеждённый монстр',
        default=1
    )
    # Классы, к которым не равнодушен монстр
    not_indifferent_klasses = models.ManyToManyField(
        KlassCard,
        through='KlassRelationShip'
    )
    # Расы, к которым не равнодушен монстр
    not_indifferent_races = models.ManyToManyField(
        RaceCard,
        through='RaceRelationShip'
    )
    must_find_other_gender_munchkin = models.BooleanField(
        'Ты должен искать помощи у манчкина другого пола',
        default=False
    )
    weapon_is_unactive_in_next_fight = models.BooleanField(
        'Твоё оружие бесполезно в следущем бою',
        default=False
    )
    not_must_fight = models.BooleanField(
        'Можешь биться по желанию',
        default=False
    )
    is_damage_modificator_cube = models.BooleanField(
        'Манчкин теряет столько уровней, сколько выпало на кубике',
        default=False
    )
    damage_lost_class_and_race = models.BooleanField(
        'Манчкин теряет все карты рас и классов',
        default=False
    )
    esc_auto = models.BooleanField(
        'Автоматическая смывка от этого монстра',
        default=False
    )
    double_damage_from_fire = models.BooleanField(
        'Огненные шмотки наносят этому монстру двойной урон',
        default=False
    )
    power_modificator_assistant = models.SmallIntegerField(
        'Модификатор силы монстра в зависимости от наличия помощника у манчкина',
        default=0
    )
    dont_touch_level = models.SmallIntegerField(
        'Уровень манчкинов, с которого преследует этот монстр',
        default=1,
    )
    must_fight = models.BooleanField(
        'Должен биться, даже если обычный манчкин может не делать этого',
        default=False
    )
    can_change_treasure = models.BooleanField(
        'Манчкин может заменить две карты сокровищ с руки на две из колоды',
        default=False
    )
    # модификаторы при поражении
    gender_modificator = models.SmallIntegerField(
        'Сколько уровней теряет манчкин в зависимости от пола',
        default=0,
    )
    lost_cards = models.BooleanField(
        'Каждый соперник в порядке убывания уровня забирает у тебя одну карту',
        default=False
    )
    lost_cards_by_cube = models.SmallIntegerField(
        'Сбрось столько карт, сколько выпало на кубике',
        default=0
    )
    lost_all_cards = models.BooleanField(
        'Каждый соперник, начиная с левого забирает у тебя одну карту, оставшиеся сбрось',
        default=False
    )
    must_discard_all_cards = models.BooleanField(
        'Манчкин должен сбросить все карты с руки',
        default=False
    )
    lost_big_things = models.BooleanField(
        'Сбрось все большие шмотки',
        default=False
    )
    lost_armor = models.BooleanField(
        'Потеряй бронник',
        default=False
    )
    # модификаторы при смывке
    esc_modif_cube = models.SmallIntegerField(
        'Модификатор очков на кубике при смывке',
        default=0
    )

    def __str__(self):
        return f'Монстр { self.name } {self.level} уровня'

    def damaging(self, munchkin):
        """
        Функция вычисляющая потери манчкина от разных видов монстров
        """
        if self.name == 'Утконтикора':
            # игрок выбирает сбросить всю руку или потерять 2 уровня
            if random.choice([True, False]):
                munchkin.level_down(2)
            else:
                munchkin.lost_all_hand()
        elif self.name == 'Адвокат':
            # У тебя конфискуют имущество. Каждый соперник, начиная с левого соседа,
            # тянет по карте с твоей руки. Сбрось оставшиеся карты
            for enemy in munchkin.others():
                cards = list(munchkin.all_card_in_hand())
                if len(cards) > 0:
                    munchkin.give_card(cards[0], enemy)
            munchkin.lost_all_hand()
        elif self.name == 'Желатиновый октаэдр':
            # сбрось все свои большие шмотки
            all_big_size = TreasuresCard.objects.filter(
                munchkin=munchkin,
                is_big_size=True,
            )
            for thing in all_big_size:
                munchkin.discard(thing)
        elif self.name == '3872 Орка':
            # Брось кубик, на 1 или 2 они затаптывают тебя досмерти.
            # В остальных случаях теряешь столько уровней, сколько показал кубик
            try_dice = dice_roll()
            if try_dice in [1, 2]:
                munchkin.deading()
            else:
                munchkin.level_down(try_dice)
        elif self.name == 'Гикающий гик':
            # Стань нормальным. Сбрось из игры все свои расы и классы
            munchkin.loose_klasses()
            munchkin.loose_races()
        elif self.name == 'Невыразимо жуткий неописуемый ужас':
            # Невыразимо жуткая смерть для всех, кроме волшебника.
            # Волшебник лишается могущества - сбрось карту Волшебник
            if 'Волшебник' in munchkin.klasses():
                munchkin.klasscard_set.filter(
                    name='Волшебник').update(
                    status=enums.ON_DECK
                )
                munchkin.treasurescard_set.filter(
                    name='Волшебник'
                ).delete()
            else:
                munchkin.deading()
        elif self.name == 'Гиппогриф':
            # Ты потоптан и покусан, да ещё и растерял шмот. Начиная с правого
            # соседа, каждый игрок берет одно сокровище у тебя из игры или
            # (не глядя) с руки
            for enemy in munchkin.others():
                # TODO потом напишу
                pass
        elif self.name == 'Амазонка':
            # Потеряй все свои классы. Если у тебя нет класса, потеряй 3 уровня
            if len(munchkin.klasses()) > 0:
                munchkin.loose_klasses()
            else:
                munchkin.level_down(3)
        elif self.name == "Бульрог":
            # Ты запорот до смерти
            munchkin.deading()
        elif self.name == "Бигфут":
            # Наступает на тебя и съедает шляпу. Потеряй надетый головняк
            headdress_card = munchkin.treasurescard_set.filter(
                is_headdress=True,
                status=enums.ON_GAME
            )
            if headdress_card.exists():
                munchkin.discard(headdress_card)
            munchkin.set_level(1)
        elif self.name == "Плутониевый дракон":
            # ты зажарен и съеден. Это верная смерть
            munchkin.deading()
        else:
            munchkin.level_down(self.level_down_nom)


class TreasuresCard(Card):
    """
    Карта из колоды Сокровищ
    """
    is_headdress = models.BooleanField(
        'Карта головняка',
        default=False
    )
    is_armor = models.BooleanField(
        'Карта бронника',
        default=False
    )
    is_for_hands = models.BooleanField(
        'Шмотка в руки',
        default=False
    )
    is_footwear = models.BooleanField(
        'Обувка',
        default=False
    )
    bonus = models.PositiveSmallIntegerField(
        'номинальная сила сокровища, при наличии',
        default=0
    )
    price_nom = models.IntegerField(
        'Номинальная цена шмотки',
        default=0
    )
    is_big_size = models.BooleanField(
        'Это большая шмотка',
        default=False
    )
    how_many_hands_take = models.PositiveSmallIntegerField(
        'сколько рук занимает',
        default=0
    )
    is_one_time = models.BooleanField(
        'Это разовая шмотка',
        default=False
    )
    is_moment = models.CharField(
        'когда можно играть шмотку',
        max_length=30,
        choices=enums.WHERE_USE
    )
    # классы на которых шмотка особо действует
    for_klasses_only = models.ForeignKey(
        KlassCard,
        on_delete=models.SET_NULL,
        blank=True, null=True,
    )
    # расы на которых шмотка особо действует
    for_races_only = models.ForeignKey(
        RaceCard,
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    status = models.CharField(
        'Где находится карта',
        max_length=40,
        choices=enums.CARD_STATUS,
        default=enums.ON_DECK
    )
