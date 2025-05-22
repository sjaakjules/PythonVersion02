'''
Purpose: Interprets card rule text and enforces complex or undefined rules.
Responsibilities:
	•	Parses keywords (e.g. "Genesis", "Voidwalk") and attaches passive/triggered/activated logic.
	•	Prompts the user to define custom behavior if rules are undefined or ambiguous (The Golden Rule: "use common sense and be cool" ).
	•	Maintains a lookup table of resolved abilities and their effects.
	•	Manages insertion of triggered events into the Storyline system.
	•	Enforces rule timing: non-active player places triggered events first, player priority, and event resolution
'''


class RulesEngine:
    def __init__(self):
        self.ability_lookup = {}
        self.storyline = []  # Event queue

    def parse_keywords(self, card):
        # Parse keywords and attach logic
        pass

    def resolve_ability(self, card, ability):
        # Lookup and resolve ability
        pass

    def insert_triggered_event(self, event):
        self.storyline.append(event)

    def enforce_timing(self):
        # Enforce rule timing and event resolution
        pass
    
    def move(self, card, step, board):
        # Move card by step on board
        pass

    def fight(self, attacker, defender, board):
        # Attack with card
        pass