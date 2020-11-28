import random

from server.constants import SUIT_HEARTS
from server.constants import SUIT_DIAMONDS
from server.constants import SUIT_CLUBS
from server.constants import SUIT_SPADES


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit


class Deck:
    def __init__(self):
        self.cards = [
            Card(i + 1, suit)
            for i in range(13)
            for suit in (SUIT_HEARTS, SUIT_DIAMONDS, SUIT_CLUBS, SUIT_SPADES)
        ]
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop()
