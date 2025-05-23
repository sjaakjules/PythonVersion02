'''
Purpose: Orchestrates the overall game flow from start to finish.
Responsibilities:
	•	Manages game phases: board selection → deck selection → game start → Player turns.
	•	Calls Util_Loader to load the board and decks.
	•	Instantiates the Board and Deck classes after player input using Util_Loader.py.
	•	Maintains turn order and transitions between Start, Main, and End Phases.
	•	Sends cards and board info to Rules_engine.py to handle triggered abilities and the Storyline stack (event queue) as described in the rulebook.
	•	Tracks player state: life total, mana pool (reset per turn), and threshold levels from sites.
'''

from Util_Loader import select_game_board, select_decks
from Board import Board
from Deck import Deck
from Player import Player
from Rules_Engine import RulesEngine
from GUI_Manager import GUI_Manager


class Game_Manager:
    def __init__(self, gui_manager: GUI_Manager) -> None:
        self.gui_manager = gui_manager
        self.board = Board()
        self.players = [Player(0), Player(1)]
        self.rules_engine = RulesEngine()
        self.game_states = ["board_selection", "deck_selection", "game_start"]
        self.state = 0
        self.turn = 0

    def run(self):
        self.state = self.gui_manager.run()
        
        print("Game started!")
        while not self.is_game_over():
            while not self.start_phase():
                pass
            while not self.main_phase():
                pass
            while not self.end_phase():
                pass
            self.turn += 1

    def is_game_over(self):
        # Placeholder for win condition
        return False

    def start_phase(self):
        print(f"Start of turn {self.turn + 1}")
        # Untap all cards
        # Get mana from sites
        # Trigger start of turn abilities
        # Draw from either Spellbook or Atlas

    def main_phase(self):
        print("Main phase")
        # Player actions, card plays, etc.

    def end_phase(self):
        print("End of turn")
        # Trigger end of turn abilities
        # Damage is removed from their minions and artifacts
        # Effects that last this turn end
        # End turn