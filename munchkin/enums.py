from model_utils import Choices


# Количество карт, выдаваемых в начале игры
CARDS_ON_START = 4

# Минимальное количество игроков
MIN_GAMER_COUNT = 3

# Максимальное количество игроков
MAX_GAMER_COUNT = 6

# максимально возможное количество карт в руке
MAX_ALLOWED_CARD = 5

# Перечисление полов игороков
MALE = 'Мужской'
FEMALE = 'Женский'

GENDER = Choices(
    MALE,
    FEMALE,
)

# Перечисление статусов игры
RECRUITMENT = "Набор игроков"
DEAL_OF_CARDS = "Раздача карт"
MOVE = 'Чей-то ход'
GAME_OVER = 'Конец игры'

STATUS = Choices(
    RECRUITMENT,
    DEAL_OF_CARDS,
    MOVE,
    GAME_OVER,
    )

ON_HAND = 'в руке игрока'
ON_TREAS_DISCARD = 'карта в сбросе сокровищ'
ON_DOORS_DISCARD = 'карта в сбросе дверей'
ON_GAME = 'Карта в игре, на столе перед игроком'
ON_FIGHT = 'Карта в бою'
ON_DECK = 'Карта в колоде и не роздана'

CARD_STATUS = Choices(
    ON_HAND,
    ON_TREAS_DISCARD,
    ON_DOORS_DISCARD,
    ON_GAME,
    ON_FIGHT,
    ON_DECK,
)

ANY_TIME = 'в любое время'
IN_FIGHT = 'в бою'
IN_SELF_MOVE = 'в свой ход'
IN_ESCAPE = 'при смывке'
AFTER_EXCAPE = 'после успешной смывки'

WHERE_USE = Choices(
    ANY_TIME,
    IN_FIGHT,
    IN_SELF_MOVE,
    IN_ESCAPE,
    AFTER_EXCAPE
)
