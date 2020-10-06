from django.test import TestCase

from authapp.models import Gamer
from munchkin.exceptions import TooFewGamersForStartGame
from munchkin.game import Game
from munchkin.management.commands import fill_db
from munchkin.models import *


class TestMunchkin(TestCase):

    def setUp(self):
        # создаём игру и пользователей
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
        # загружаем карты
        fill_db.Command().handle()

    def test_init_game(self):
        gosha = Gamer.objects.get(name='gosha')
        masha = Gamer.objects.get(name='masha')
        vasya = Gamer.objects.get(name='vasya')

        game = Game.objects.create(
            title='Манчкин',
            desc='Манчкин классический'
        )
        print(f'{gosha} начинает игру {game}')
        game._init_(gosha)
        print(f'{masha} присоединяется к игре {game}')
        game.join_gamer(masha)
        # print('пытаемся начать игру с недостаточным количеством игроков')
        # with self.assertRaises(TooFewGamersForStartGame) as e:
        #     game.all_in_place()
        # the_exception = e.exception
        # self.assertEqual(the_exception.text, f'Для этой игры нужно больше '
        #                                      f'{enums.MIN_GAMER_COUNT}-х человек')
        print(f'{vasya} присоединяется к игре {game}')
        game.join_gamer(vasya)
        print('все на месте, раздаём карты')
        game.all_in_place()
        game.movement()


