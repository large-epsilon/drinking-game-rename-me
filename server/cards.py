# TODO: define apply throughout


class Card:
    # Generic card class. Subclass this for each card you want to add.

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def apply(self, state, *args):
        # Applies this card's effects to state.
        # Implement this for each card.
        raise NotImplementedError(
            "'apply' is not implemented on '{}'".format(this.name)
        )


class CardDrink(Card):
    def __init__(self):
        super().__init__("Drink", "Target player drinks.")


class CardSobrietyChip1Y(Card):
    def __init__(self):
        super().__init__(
            "1-Year Sobriety Chip",
            "The next time you would take any amount of drinks, reduce that "
            "amount by 1.",
        )


def build_deck():
    cards_in_deck = [
        (10, CardDrink),
        (10, CardSobrietyChip1Y),
    ]

    deck = {}

    for count, card_type in cards_in_deck:
        for i in range(count):
            card_id = "".join(
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(10)
            )
            deck[card_id] = card_type()

    return deck
