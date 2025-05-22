'''
Purpose: Manages player state and interactions.
Responsibilities:
	•	Tracks player life, mana, and thresholds.
	•	Has hand, deck, and cemetery.
'''
import Deck
import Card


class Player:
    def __init__(self, id):
        self.id = id
        self.life = 20
        self.mana = 0
        self.thresholds = {}
        self.hand = []  # list of cards in hand
        self.deck = Deck()  # Deck object
        self.graveyard = []  # list of cards in graveyard

