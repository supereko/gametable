import random

from django.db import models

from mainapp.models import BaseGame
from munchkin import enums
from munchkin.exceptions import TooFewGamersForStartGame, TooManyGamersForStartGame
from munchkin.models import Munchkin, MonsterCard, KlassRelationShip, RaceRelationShip, ModificatorCard, dice_roll, \
    OtherCard, CurseCard


class Fighting(models.Model):
    """
    Класс для описания боя, перечисляет дерущиеся стороны
    и их модификаторы
    """
    munchkins = models.ManyToManyField(
        'Munchkin',
    )
    monsters = models.ManyToManyField(
        MonsterCard,
    )
    munchkin_modifs = models.ManyToManyField(
        ModificatorCard,
        related_name='munchkin_modifs'
    )
    monster_modifs = models.ManyToManyField(
        ModificatorCard,
        related_name='monster_modifs'
    )
    reward_tres = models.SmallIntegerField(
        'Количество сокровищ в награду помощнику',
        default=0
    )
    reward_level = models.SmallIntegerField(
        'Количество уровней в награду помощнику',
        default=0
    )
    is_need_help = models.BooleanField(
        'Нужна ли манчкину помощь',
        default=False
    )

    def __str__(self):
        munchkins = self.munchkins.all().refetch_related("munchkins")
        monsters = self.monsters.all().refetch_related("monsters")
        return f'Бой {", ".join(munchkin.name for munchkin in munchkins)} c ' \
               f'{", ".join(monster.name for monster in monsters)}'

    def get_assistant(self):
        """
        Функция для получения помощи в битве с монстрами
        """
        # TODO можно воткнуть проверку на количество манчкинов в битве,
        # чтоб не получить второго помощника
        munchkin = self.munchkins.first()
        # пока нет интерфейса выбираем случайным образом
        assistant = random.choice(munchkin.others())
        self.reward()
        print(f'Призван помощник {assistant}')
        return assistant

    def reward(self):
        """
        Функция для вычисления награды помощничку, выдаёт
        случайное количество сокровищ и уровней,
        TODO временное решение, переписать, когшда появится интерфейс игрока
        """
        monsters = self.monsters.all()
        all_tres = sum(monster.treasure_count for monster in monsters)
        all_levels = sum(monster.treasure_count for monster in monsters)
        self.reward_tres = random.randint(0, all_tres)
        self.reward_level = random.randint(0, all_levels)

    def _init_(self, monster, munchkin):
        """
        Функция инициализации боя
        """
        self.monsters.add(monster)
        self.munchkins.add(munchkin)
        # манчкин ищет помощника, если этого требует монстр
        if monster.must_find_other_gender_munchkin:
            assistant = random.choice(
                munchkin.select_assistants_other_gender()
            )
            if assistant:
                self.munchkins.add(assistant)
                self.reward()
        print(f'Инициализирован бой с участниками '
              f'{self.munchkins.all()} {self.monsters.all()}')

    @property
    def monsters_power(self):
        monsters = self.monsters.all()
        munchkins = self.munchkins.all()
        munchkin_klasses = [klass for munchkin in munchkins for klass in munchkin.klasses()]
        munchkin_races = [race for munchkin in munchkins for race in munchkin.races()]
        print('Расы и классы манчкинов этого боя')
        print(munchkin_klasses, munchkin_races)
        for monster in monsters:
            # проверяем, есть ли у монстра предпочтения по расе или классу
            klrships = KlassRelationShip.objects.filter(
                monster=monster,
                klass__in=munchkin_klasses
            )
            rarships = RaceRelationShip.objects.filter(
                monster=monster,
                race__in=munchkin_races
            )
            if klrships.exists():
                monster.level += sum(
                    klrship.power_modificator
                    for klrship in klrships.all()
                )
            if rarships.exists():
                monster.level += sum(
                    rarship.power_modificator
                    for rarship in rarships.all()
                )
        monster_modifs = self.monster_modifs.all()
        return sum(monster.level for monster in monsters) + \
               sum(modif.bonus for modif in monster_modifs)

    @property
    def munchkins_power(self):
        munchkins = self.munchkins.all()
        munchkin_modifs = self.munchkin_modifs.all()
        print(f'Усилители манчкинов {munchkin_modifs}')
        # Воин побеждает при равенстве сил
        plus = 1 if 'Воин' in [munchkin.klasses() for munchkin in munchkins] else 0
        return sum(munchkin.power for munchkin in munchkins) + \
               sum(modif.bonus for modif in munchkin_modifs) + plus

    @property
    def monsters_level_up(self):
        return sum([monster.level_up_nom for monster in self.monsters.all()])

    @property
    def monsters_treasures(self):
        return sum([monster.treasure_count for monster in self.monsters.all()])

    def fight(self):
        """
        Функция для сравнения сил монстра и манчкинов в битве,
        то есть другие манчкины в цикле подбрасывают дополнительные
        карты, пока последний из них не откажется от её продолжения
        возвращает False в случае поражения манчкинов,
        True в случае победы и объект манчкина-помощника, если он был
        """
        # Манчкин, вступивший в бой первым
        munchkin = self.munchkins.first()
        if self.munchkins.count() > 1:
            # TODO Здесь грабли чувствую я
            assistant = self.munchkins.last()
        else:
            assistant = None
        # противнички
        enemies = munchkin.others(assistant=assistant)
        while enemies.exists():
             # перебираем злодеев
            print(f'Список врагов: {enemies}')
            for enemy in enemies:
                # они по очереди пытаются подкинуть монстра
                new_monster = enemy.try_to_throw_monster()
                if new_monster:
                    self.monsters.add(new_monster)
                # или модифицировать имеющихся
                new_modif = enemy.try_to_throw_modif()
                if new_modif:
                    self.monster_modifs.add(new_modif)
                # Вор может попытаться подрезать манчкина, сбросив карту
                # выбираем жертву
                victim = random.choice([munchkin for munchkin in self.munchkins.all()])
                if all([
                    'Вор' in enemy.klasses(),
                    victim.undercut_count < 1,
                    random.choice([True, False])
                    ]):
                    # выбираем карту с руки
                    card = random.choice(
                        munchkin.doors_card_in_hands().union(
                            munchkin.treasures_card_in_hands()
                        )
                    )
                    victim.undercut_count += 1
                    # сбрасываем карту
                    munchkin.discard(card)
                    victim.power = victim.power - 2
                # TODO здесь ещё можно наложить проклятие
            # перебираем защищающихся
            for munchkin in self.munchkins.all():
                new_modif = munchkin.try_to_throw_modif()
                if new_modif:
                    self.munchkin_modifs.add(new_modif)
                monsters = self.monsters.all()
                munchkin_klasses = [
                    munchkin.klasses() for munchkin in self.munchkins.all()
                ]
                munchkin_races = [
                    munchkin.races() for munchkin in self.munchkins.all()
                ]
                power_plus = 0
                # Если один из манчкинов клирик, а один из монстров андед,
                # и манчкин решил этим воспользоваться менее чем в третий раз
                if all([
                    True in [monster.is_undead for monster in monsters],
                    "Клирик" in munchkin_klasses,

                    ]):
                    # можно получить +3 к силе, сбросив карту
                    power_plus += 3
                elif all([
                        "Воин" in munchkin_klasses,
                        munchkin.discard_count < 3,
                        random.choice([True, False])
                    ]):
                    # можно получить +1 к силе, сбросив карту
                    power_plus += 1
                # если есть преимущества класса и манчкин желает ими воспользоваться
                if all([
                    power_plus > 0,
                    munchkin.discard_count < 3,
                    random.choice([True, False])
                ]):
                    # выбираем карту с руки
                    card = random.choice(
                        munchkin.doors_card_in_hands().union(
                        munchkin.treasures_card_in_hands()
                        )
                    )
                    munchkin.discard_count += 1
                    munchkin.discard(card)
                    munchkin.power = munchkin.power + power_plus
                # делаем запрос манчкину, не хочет ли он сыграть
                # монстра с руки как одноразвую иллюзию, при условии,
                # что монстр у него есть и нет помощника
                elif all([
                    "Гном" in munchkin_races,
                    assistant is None,
                    munchkin.have_monsters(),
                    random.choice([True, False])
                ]):
                    # выбираем монстра
                    illusion = random.choice(munchkin.monstercard_set.all())
                    munchkin.discard(illusion)
                    munchkin.power = munchkin.power + illusion.level
            # если до сих пор нет помощника, не пора ли позвать
            is_need_help = random.choice([False, True])
            if assistant is None and is_need_help:
                assistant = self.get_assistant()
            # предоставляем возможность злодеям отказаться от продолжения
            # битвы или обратно вернуться к злодействам, если отказались ранее
            for enemy in enemies:
                enemy.is_want_to_continue_fight()
            enemies = munchkin.others(assistant=assistant).filter(
                is_want_to_continue=True)
        # бой окончен выводим характеристики сторон
        print(f'Сила всех манчкинов боя {self.munchkins_power}')
        print(f'Сила всех монстров боя {self.monsters_power}')
        # очищаем счетчики
        self.munchkins.update(undercut_count=0)
        self.munchkins.first().others(assistant=assistant).update(discard_count=0)
        # Побеждает та сторона, которая сильнее
        win = self.munchkins_power > self.monsters_power
        if win:
            print(f'Побеждает {self.munchkins.all()}')
        else:
            print(f'Побеждает {self.monsters.all()}')
        # считаем прибыль
        profit = dict()
        if win:
            print(f'{self.munchkins.all()} победа над {self.monsters.all()}')
            levels = self.monsters_level_up - self.reward_level
            treasures = self.monsters_treasures - self.reward_tres
            profit[self.munchkins.first()] = {
                'levels': levels,
                'treasure_count': treasures
            }
            if assistant:
                # эльфы получают +1 уровень за каждого монстра, которго помогли убить
                adv_level = 1 * self.monsters.count() if 'Эльф' in assistant.races() else 0
                profit[assistant] = {
                    'levels': self.reward_level + adv_level,
                    'treasure_count': self.reward_tres
                }
        else:
            profit[self.munchkins.first()] = {}
            if assistant:
                profit[assistant] = {}
        return win, profit

    def escape(self, munchkin):
        """
        Функция для попыток смыться от всех монстров боя
        """
        for monster in self.monsters.all():
            # бросаем кубик на смывку
            cube = dice_roll()
            if 'Эльф' in munchkin.races():
                cube += 1
            if all([
                'Волшебник' in munchkin.klasses(),
                random.choice([True, False])
                ]):
                # можно сбросить до 3-ёх карт после броска на смывку, каждая даёт +1
                # если игрок соглашается сбросить очередную карту
                # сколько карт скидываем
                cards_count = random.randint(1, 3)
                cards_for_discard = random.sample(
                    list(
                        munchkin.all_card_in_hand()
                    ),
                    cards_count
                )
                for card in cards_for_discard:
                    munchkin.discard(card)
                cube += cards_count
            if cube > 3:
                # получилось
                result = True
            # Хафлинг, провалив первый бросок смывки, может сбросить карту для второй попытки
            elif all([
                'Хафлинг' in munchkin.races(),
                random.choice([True, False])
                ]):
                munchkin.discard(random.choice(
                    list(munchkin.all_card_in_hand()))
                )
                if dice_roll() > 3:
                    # получилось
                    result = True
                else:
                    result = False
                    monster.damaging(munchkin)
            else:
                # не получилось - терпим непотребство от этого монстра
                result = False
                monster.damaging(munchkin)
            if result:
                print(f'У {munchkin} получилось сбежать')
            else:
                print(f'Терпим непотребство от {monster}')
            return result


class Game(BaseGame):
    """
    Класс описывающий игру Манчкин с классическим набором карт
    """
    status = models.CharField(choices=enums.STATUS, max_length=20)
    members = models.ManyToManyField(
        'authapp.Gamer',
        through='authapp.Membership'
    )

    def __str__(self):
        return f'{self.title} - {self.status}'

    def _init_(self, init_user):
        """
        Функция инициализации игры, создаётся новая игра,
        ожидающая присоединения остальных участников
        """
        self.status = enums.RECRUITMENT
        self.next_munchkin = None
        self.join_gamer(init_user)

    def join_gamer(self, new_gamer):
        """
        Функция, присоединяющая нового манчкина к игре и
        определяющая кто за кем ходит
        new_gamer - Gamer object
        """
        if self.status == enums.RECRUITMENT:
            munchkin = Munchkin.objects.create(
                gamer=new_gamer,
                game=self,
            )
            if self.members.count() > 0:
                prev_munchkin = self.members.order_by(
                    'membership__datetime_joined'
                ).last().munchkin
                prev_munchkin.next = munchkin
                prev_munchkin.save()
            from authapp.models import Membership
            ms = Membership.objects.create(
                gamer=new_gamer,
                game=self,
            )
            self.membership_set.add(ms)
            try:
                if self.members.count() > enums.MAX_GAMER_COUNT:
                    self.all_in_place()
                    raise TooManyGamersForStartGame(f'Количество игроков достигло максимального '
                                                    f'значения {enums.MAX_GAMER_COUNT} игроков')
            except TooManyGamersForStartGame as e:
                print(e)
        else:
            print('Эта игра уже идёт без вас или окончена')

    def dealing_of_cards(self):
        """
        Функция, раздающая карты игрокам в начале игры
        """
        Munchkin.objects.filter(game=self)
        members = Munchkin.objects.filter(game=self)
        for member in members:
            print()
            print(member)
            door_cards = member.get_doors_card(enums.CARDS_ON_START)
            treas_card = member.get_treas_card(enums.CARDS_ON_START)
            print(f'        {door_cards} {treas_card}')
        # случайно выбираем того, с кого начинается игра
        next_munchkin = random.choice(members)
        next_munchkin.is_next_move = True
        next_munchkin.save()
        return next_munchkin

    def all_in_place(self):
        """
        Функция окончания набора манчки`нов для игры, проверяет
        количество игроков, тасует колоды, раздаёт карты
        """
        members = self.members.all()
        try:
            if members.count() < enums.MIN_GAMER_COUNT:
                raise TooFewGamersForStartGame(f'Для этой игры нужно больше '
                                               f'{enums.MIN_GAMER_COUNT}-х человек')
        except TooFewGamersForStartGame as e:
            print(e)
        else:
            self.status = enums.DEAL_OF_CARDS
            # замыкаем круг игроков, инициатор игры теперь
            # следует за последним присоединившимся
            first_munchkin = self.members.order_by(
                'membership__datetime_joined'
            ).first().munchkin
            last_munchkin = self.members.get(
                munchkin__next__isnull=True
            ).munchkin
            last_munchkin.next = first_munchkin
            last_munchkin.save()
            # раздаём карты и выясняем чей ход
            print('Идет раздача карт игрокам')
            self.next_munchkin = self.dealing_of_cards()
            # желающие могут сбросить карты, поменять, продать карты
            for member in members:
                self.card_relocation(member.munchkin)
            self.status = enums.MOVE
            self.save()

    def movement(self):
        # игрок
        munchkin = self.next_munchkin
        print(f'Ходит {munchkin}')
        # делает первый ход в открытую и решает
        # сыграть монстра с руки
        if munchkin.have_monsters():
            # игрок выбирает какого монстра сыграть с руки
            monster = munchkin.monstercard_set.first()
            card = random.choice([False, monster])
            if card:
                print(f'{munchkin} призывает монстра {card} с руки')
            else:
                card = munchkin.get_doors_card(1)[0]
        # или вышибить дверь
        else:
            card = munchkin.get_doors_card(1)[0]
            print(f'{munchkin} вышибает дверь, за ней {card}: {card.description}')
        if isinstance(card, MonsterCard):
            monster = card
            fighting = Fighting.objects.create()
            fighting._init_(monster, munchkin)
            # игрок выбирает биться или убегать
            fight = random.choice([True, False])
            # если деремся
            if fight:
                print(f'{munchkin} принимает бой')
                win, profit = fighting.fight()
                # если победили, делим сокровища и уровни
                if win:
                    for winner, profit in profit.items():
                        winner.level_up(profit['levels'], win=True)
                        winner.get_treas_card(profit['treasure_count'])
                        # даем возможность манчкину обналичить взятые уровни
                        get_level_card = winner.othercard_set.filter(
                            name='Получи уровень'
                        )
                        if get_level_card.exists() and random.choice([True, False]):
                            get_level_card = get_level_card.first()
                            winner.othercard_set.remove(get_level_card)
                            winner.discard(get_level_card)
                            winner.level_up(1)
            # Если убегаем или бились и не победили пытаемся смыться по очереди
            else:
                losers = fighting.munchkins.all()
                for loser in losers:
                    fighting.escape(loser)
        elif isinstance(card, OtherCard):
            if card.name == 'Божественное вмешательство':
                for munchkin in Munchkin.objects.all():
                    if 'Клирик' in munchkin.klasses():
                        munchkin.level_up(1, win=True)
            else:
                # Любую другую карту показываем всем
                card.status = enums.ON_DECK
                card.save()
                # затем забираем себе
                munchkin.take_card(card)
        elif isinstance(card, CurseCard):
            munchkin.curse_run(card)
        else:
            # Любую другую карту показываем всем
            card.status = enums.ON_DECK
            card.save()
            # затем забираем себе
            munchkin.take_card(card)
        # игрок делает второй ход в закрытую и берет эту карту в руку
        card = munchkin.get_doors_card(1)
        end_of_move = False
        while not end_of_move:
            for munchkin in Munchkin.objects.filter(game=self):
                # даем возможность манчкинам украсть уровни
                stole_level_card = munchkin.othercard_set.filter(
                    name='Укради уровень'
                )
                # если есть карта Укради уровень, есть желание красть и есть у кого красть
                if all([
                    stole_level_card.exists(),
                    random.choice([True, False]),
                    munchkin.others().filter(level__gt=1).exists()
                ]):
                    munchkin.othercard_set.remove(stole_level_card)
                    munchkin.discard(stole_level_card)
                    victim = random.choice(munchkin.others().filter(level__gt=1))
                    victim.level_down(1)
                    munchkin.level_up(1)
                self.card_relocation(munchkin)
            # проверяем количество карт на руках игроков
            end_of_move = all([
                member.munchkin.place_in_hands()
                for member in self.members.all()
            ])
            while not end_of_move:
                for member in self.members.all():
                    if not member.munchkin.place_in_hands():
                        member.munchkin.discard(
                            random.choice(
                                list(member.munchkin.all_card_in_hand())
                            )
                        )
                end_of_move = all([
                    member.munchkin.place_in_hands()
                    for member in self.members.all()
                ])
            # окончание хода, выводим характеристики игроков, чтоб
            # сработала функция подсчета уровня и возбудилось исключение
            # окончания игры при достижении кем-то 10-ого уровня
        print(f'Окончание хода - {munchkin}')
        self.next_munchkin = munchkin.next
        self.movement()

    def card_relocation(self, munchkin):
        """
        Функция для обмена, продажи, сброса карт
        """
        # даем возможность манчкину наложить проклятие при наличии
        # проклятия и желания его наложить
        if random.choice([True, False]) and munchkin.cursecard_set.exists():
            victim = random.choice(munchkin.others())
            munchkin.set_curse(victim)
        # даем возможность манчкину что-то продать
        if random.choice([True, False]):
            munchkin.sell_out()
        # с кем то поменяться, если есть такое желание и есть чем меняться
        if random.choice([True, False]) and \
                list(munchkin.all_card_in_hand()) != []:
            # тут предварительно договариваемся, и другой манчкин
            # в свою возможность поменяться отдаёт этой же функцией
            # оговоренную карту (карты)
            other_munchkin = random.choice(munchkin.others())
            # выбираем карту, которую отдаем
            card = random.choice(list(munchkin.all_card_in_hand()))
            munchkin.give_card(card, other_munchkin)
        # выложить карты с руки в игру
        for card in munchkin.all_card_in_hand():
            if random.choice([True, False]):
                munchkin.from_hand_on_game(card)
        # вор может сбросить карту и бросить кубик, чтобы попытаться
        # украсть у соперника добытую мелкую шмотку
        if 'Вор' in munchkin.klasses() and random.choice([True, False]):
            victim = random.choice(munchkin.others())
            munchkin.discard(random.choice(list(munchkin.all_card_in_hand())))
            # кража удалась
            if dice_roll() > 3:
                card = random.choice(list(victim.treasurescard_set.all()))
                victim.give_card(card)
            else:
                # на кубике меньше 4 - теряем уровень
                munchkin.level_down(1)
        # просто скинуть карту в сброс
        if random.choice([True, False]) and \
                list(munchkin.all_card_in_hand()) != []:
            # игрок выбирает карту, которую скинуть
            card = random.choice(list(munchkin.all_card_in_hand()))
            munchkin.discard(card)
