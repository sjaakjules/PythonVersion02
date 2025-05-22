'''
Purpose: Encapsulates each player's deck operations.
Responsibilities:
	•	Manages:
	•	Atlas (sites)
	•	Spellbook (spells)
	•	Hand (drawn cards)
	•	Cemetery (destroyed cards)
	•	Enforces mulligan rules, search and draw and return cards to deck and shuffling after searches
'''

import random
from Card import Card


class Deck:
    def __init__(self, cards):
        self.atlas = [card for card in cards if card.card_type == 'Site']
        self.spellbook = [card for card in cards if card.card_type in ['Magic', 'Aura', 'Artifact']]
        self.hand = []
        self.cemetery = []
        self.library = [card for card in cards if card.card_type not in ['Site']]
        random.shuffle(self.library)

    def draw(self, n=1):
        for _ in range(n):
            if self.library:
                self.hand.append(self.library.pop())

    def mulligan(self):
        # Simple mulligan: shuffle hand back and redraw
        self.library.extend(self.hand)
        self.hand = []
        random.shuffle(self.library)
        self.draw(7)

    def search(self, condition):
        # Return cards matching a condition
        return [card for card in self.library if condition(card)]

    def return_to_deck(self, card):
        self.library.append(card)
        random.shuffle(self.library)

    def shuffle(self):
        random.shuffle(self.library)