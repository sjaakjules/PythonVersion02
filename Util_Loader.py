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
from GUI_Manager import setup_board_selection_screen
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


def select_game_board() -> str:
    """
    Show game board selection screen and return the selected board path.
    
    Returns:
        str: Path to the selected board image
    """
    # Show game board selection screen.
    #   - get all images in BACKGROUND_ASSET_DIR, not subfolders, and display them in a scrollable grid.
    board_options = setup_board_selection_screen()
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


def extract_deck_id(url_or_id: str) -> str:
    """
    Extract the deck ID from a Curiosa URL or ID.
    
    Args:
        url_or_id (str): Full URL or deck ID
        
    Returns:
        str: The deck ID
    """
    if '/' in url_or_id:
        return url_or_id.rstrip('/').split('/')[-1]
    return url_or_id


def get_curiosa_deck(deck_url_or_id: str) -> Dict[str, Any]:
    """
    Fetch deck data from Curiosa API.
    
    Args:
        deck_url_or_id (str): Full URL or deck ID
        
    Returns:
        Dict[str, Any]: Deck data from Curiosa API
    """
    deck_id = extract_deck_id(deck_url_or_id)
    url = f"{CORS_PROXY}{CURIOSA_API_BASE}{deck_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_all_cards_metadata() -> List[Dict[str, Any]]:
    """
    Fetch or load from cache all card metadata from Sorcery API.
    
    Returns:
        List[Dict[str, Any]]: List of card metadata
    """
    if os.path.exists(CARD_DATA_PATH):
        with open(CARD_DATA_PATH, 'r') as f:
            all_data = json.load(f)
    else:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(CARD_DATA_PATH), exist_ok=True)
        
        # Fetch and save data
        response = requests.get(SORCERY_API)
        all_data = response.json()
        
        with open(CARD_DATA_PATH, 'w') as f:
            json.dump(all_data, f, indent=4, sort_keys=True)

    return all_data


def match_curiosa_to_sorcery(curiosa_cards: List[Dict[str, Any]], 
                             all_sorcery_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Match Curiosa cards with Sorcery API card data.
    
    Args:
        curiosa_cards (List[Dict[str, Any]]): Cards from Curiosa
        all_sorcery_cards (List[Dict[str, Any]]): All cards from Sorcery API
        
    Returns:
        List[Dict[str, Any]]: Matched cards with full details
    """
    matched = []
    for card in curiosa_cards:
        name = card["name"].strip().lower()
        match = next((c for c in all_sorcery_cards if c["name"].strip().lower() == name), None)
        if match:
            matched.append({
                "name": card["name"],
                "quantity": card["quantity"],
                "img_url": card["src"],
                "details": match
            })
        else:
            print(f"❌ Not found in API: {card['name']}")
    return matched


def get_deck_json_from_curiosa(deck_url: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get full deck data from Curiosa and match with Sorcery API.
    
    Args:
        deck_url (str): URL of the deck on Curiosa
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: Full deck data with matched card details
    """
    curiosa_data = get_curiosa_deck(deck_url)
    
    with open("tmp/curiosa_deck.json", 'w') as f:
        json.dump(curiosa_data, f, indent=4, ensure_ascii=False)
        
    sorcery_cards = fetch_all_cards_metadata()

    full_deck = {}
    for section in ["avatar", "atlas", "spellbook", "sideboard"]:
        matched_cards = match_curiosa_to_sorcery(curiosa_data.get(section, []), sorcery_cards)
        full_deck[section] = matched_cards

    with open("tmp/full_deck.json", 'w') as f:
        json.dump(full_deck, f, indent=4, ensure_ascii=False)
        
    return full_deck