'''
Purpose: Manages game setup and asset loading.
Responsibilities:
	•	Loads game boards and user-selected decks.
	•	Interfaces with local files or APIs to fetch card definitions and images.
	•	Prepares data for Deck, Board, and Card classes.
	•	Handles card image loading and caching.
'''

import json
import os
import requests
from typing import Dict, List, Optional, Tuple, Union, Any
import GUI_Manager as GUI
from Card import Card
from Deck import Deck
from Board import Board
from Util_Config import BACKGROUND_ASSET_DIR, BACKCARD_ASSET_DIR
from Curiosa_Decks import (
    PRECON_ALPHA, PRECON_BETA,
    SINGLE_ELEMENT, DOUBLE_ELEMENT,
    TRIPLE_ELEMENT, QUADRUPLE_ELEMENT,
    get_avatar_decks, get_available_avatars
)

CORS_PROXY = "https://corsproxy.innkeeper1.workers.dev/?url="
CURIOSA_API_BASE = "https://curiosa.io/api/decks/"
SORCERY_API = "https://api.sorcerytcg.com/api/cards"
CARD_DATA_PATH = "data/CardList.json"


def select_game_board(gui: GUI) -> str:
    """
    Show game board selection screen and return the selected board path.
    
    Returns:
        str: Path to the selected board image
    """
    # Show game board selection screen.
    #   - get all images in BACKGROUND_ASSET_DIR, not subfolders, and display them in a scrollable grid.
    
    #   - As the user moves their mouse around, if it hovers over one, the image pulses. 
    #   - The user clicks on one, the image grows to 50% of the screen as an overlay, if clicked again it is selected, 
    #     if outside image selected it disapears showing the grid of images.
    return board_options


def select_decks() -> Tuple[str, str]:
    """
    Show deck selection screen and return the selected deck URLs.
    
    Returns:
        Tuple[str, str]: URLs for player 1 and player 2's selected decks
    """
    # Start Deck selection screen. 
    # Selection screen shows a text box for user to paste in curiosa url to load deck. this calls "get_deck_json_from_curiosa(deck_url)"
    # Under text box are two tabs, one for precon, one for constructed, default is precon.
    # each tab has tumbnails of the decks from loading the avatar image of the deck from "get_deck_json_from_curiosa(deck_url)"
    # with precon selected there are 8 thumbnails, two rows of 4 where first 4 are alpha and second 4 are beta. the thumbnails are the avatars of each deck.
    # With constructed selected there are numerous tumbnails for each constructed deck. it is initally sorted by number of elements in 
    # the deck where there are 4 columns for 1 element, 2 elements etc etc. the user can use the scroll wheel to scroll each column of thumbnails 
    # The user can select to sort the constructed decks by avatar where there are multiple columns for each avatar, the user can use the scroll wheel 
    # to move it left to right to see all the different avatars per column.
    # The user can select a deck and click a button to load the deck.
    return "", ""


def load_decks(player1_deck: Optional[str] = None, player2_deck: Optional[str] = None) -> Tuple[Deck, Deck]:
    """
    Load decks for both players. If no decks are specified, use default precon decks.
    
    Args:
        player1_deck (Optional[str]): URL or ID for player 1's deck
        player2_deck (Optional[str]): URL or ID for player 2's deck
    
    Returns:
        Tuple[Deck, Deck]: (player1_deck, player2_deck) as Deck objects
    """
    # If no decks specified, use default precon decks
    if not player1_deck:
        player1_deck = PRECON_ALPHA['avatar_air']
    if not player2_deck:
        player2_deck = PRECON_BETA['sparkmage']
    
    # Load deck data from Curiosa
    deck1_data = get_deck_json_from_curiosa(player1_deck)
    deck2_data = get_deck_json_from_curiosa(player2_deck)
    
    # Convert deck data to Card objects and create Deck instances
    deck1_cards: List[Card] = []
    deck2_cards: List[Card] = []
    
    # Process deck 1
    for section in ['avatar', 'atlas', 'spellbook']:
        for card_data in deck1_data.get(section, []):
            for _ in range(card_data['quantity']):
                card = Card(
                    name=card_data['name'],
                    cost=card_data['details'].get('cost', 0),
                    thresholds=card_data['details'].get('thresholds', {}),
                    stats=card_data['details'].get('stats', {}),
                    card_type=card_data['details'].get('type', 'Unknown'),
                    subtypes=card_data['details'].get('subtypes', []),
                    states=set(card_data['details'].get('states', []))
                )
                deck1_cards.append(card)
    
    # Process deck 2
    for section in ['avatar', 'atlas', 'spellbook']:
        for card_data in deck2_data.get(section, []):
            for _ in range(card_data['quantity']):
                card = Card(
                    name=card_data['name'],
                    cost=card_data['details'].get('cost', 0),
                    thresholds=card_data['details'].get('thresholds', {}),
                    stats=card_data['details'].get('stats', {}),
                    card_type=card_data['details'].get('type', 'Unknown'),
                    subtypes=card_data['details'].get('subtypes', []),
                    states=set(card_data['details'].get('states', []))
                )
                deck2_cards.append(card)
    
    # Create Deck instances
    deck1 = Deck(deck1_cards)
    deck2 = Deck(deck2_cards)
    
    return deck1, deck2
