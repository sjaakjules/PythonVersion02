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
from Card import Card
from Deck import Deck
from Board import Board
from Util_Config import BACKGROUND_ASSET_DIR, BACKCARD_ASSET_DIR


CORS_PROXY = "https://corsproxy.innkeeper1.workers.dev/?url="
CURIOSA_API_BASE = "https://curiosa.io/api/decks/"
SORCERY_API = "https://api.sorcerytcg.com/api/cards"
CARD_DATA_PATH = "data/CardList.json"

def load_board(board):
    # Placeholder: return a new Board
    return Board()

def load_decks():
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
    


def extract_deck_id(url_or_id):
    if '/' in url_or_id:
        return url_or_id.rstrip('/').split('/')[-1]
    return url_or_id


def get_curiosa_deck(deck_url_or_id):
    deck_id = extract_deck_id(deck_url_or_id)
    url = f"{CORS_PROXY}{CURIOSA_API_BASE}{deck_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_all_cards_metadata():
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

    return all_data  # [Card(data) for data in all_data]


def match_curiosa_to_sorcery(curiosa_cards, all_sorcery_cards):
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


def get_deck_json_from_curiosa(deck_url):
    curiosa_data = get_curiosa_deck(deck_url)
    
    with open("tmp/curiosa_deck.json", 'w') as f:
        json.dump(curiosa_data, f, indent=4, ensure_ascii=False)
        
    sorcery_cards = fetch_all_cards_metadata()

    full_deck = {}
    for section in ["avatar", "atlas", "spellbook", "sideboard"]:
        #print(f"\n🗂️ {section.title()}:")
        matched_cards = match_curiosa_to_sorcery(curiosa_data.get(section, []), sorcery_cards)
        full_deck[section] = matched_cards

        for card in matched_cards:
            # print(f"- {card['name']} x{card['quantity']}")
            guardian = card["details"].get("guardian", {})
            # print(f"    Type: {guardian.get('type')} | Cost: {guardian.get('cost')} | Text: {guardian.get('rulesText')}")

    with open("tmp/full_deck.json", 'w') as f:
        json.dump(full_deck, f, indent=4, ensure_ascii=False)
        
    return full_deck