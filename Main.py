'''
sorcery_game/
│
├── assets/                  # Place card images here (downloaded or linked)
├── data/
│   └── card_data.json       # Cached copy of API data (optional)
└── Main.py                  # Entry point
 ├── GUI_Manager.py           # Monitors the user input and updates the game state
 └── Game_Manager.py          # Core game loop and logic
  ├── Board.py                 # 4x5 Grid and placement logic
  ├── Rules_Engine.py          # Rules engine for the game
  └── Deck.py                  # Deck data structures and player interaction logic
   └── Card.py                  # Card data structures and rule logic
└── Util_Config.py           # Constants like Font and colors
└── Util_Effects.py          # Functions that apply effects to images, fonts, icons on screen
└── Util_Loader.py           # Functions to load game board and decks.
 └── Curiosa_Decks.py         # Sample URLs for precon and custom decks loaded from curiosa website

Purpose: Entry point for launching the game.
Responsibilities:
	•	Calls the GameManager to begin the game loop via game.run().
	•	Handles any top-level exceptions or session logging.

'''

from Game_Manager import Game_Manager
from GUI_Manager import GUI_Manager

if __name__ == "__main__":
        
    gui_manager = GUI_Manager()
    game = Game_Manager(gui_manager)
    game.run()
    