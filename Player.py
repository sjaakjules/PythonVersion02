'''
Purpose: Manages player state and interactions.
Responsibilities:
	•	Tracks player life, mana, and thresholds.
	•	Has hand, deck, and cemetery.
'''
from Deck import Deck
from Card import Card


class Player:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.life: int = 20
        self.mana: int = 0
        self.thresholds: dict[str, int] = {}
        self.hand: list[Card] = []  # list of cards in hand
        self.deck: Deck = None  # Deck object
        self.graveyard: list[Card] = []  # list of cards in graveyard

