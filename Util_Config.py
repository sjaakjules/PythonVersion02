'''
Purpose: Stores game-wide constants and styling presets.
Responsibilities:
	•	Player color themes (Red, Blue)
	•	Element color mapping (Air, Earth, Fire, Water)
	•	Font types, UI backgrounds
	•	inDebugMode toggle for development
'''

import pygame

pygame.init()  # Initialize pygame
pygame.display.init()
pygame.font.init()

FPS = 60

COLOURS = {
	'Player 1': '#a1dc62',  # Green
	'Player 2': '#ad63ea',  # Purple
    'Grid': '#ffe175',  # Yellow
}

ELEMENT_COLORS = {
    'Air': '#9ebbd2',
    'Earth': '#a2a170',
    'Fire': '#e24d17',
    'Water': '#2eb2ea',
}

# Default pygame fonts: 'arial', 'helvetica', 'courier', 'freesans', 'freemono'
FONTS = {
    'title': pygame.font.SysFont('arial', 48, bold=True),
    'subtitle': pygame.font.SysFont('arial', 32),
    'selection': pygame.font.SysFont('arial', 36),
    'debug': pygame.font.SysFont('arial', 16),
    'subtle': pygame.font.SysFont('arial', 16, italic=True),  # Same as artist font
    'text': pygame.font.SysFont('arial', 22)  # New font for player labels
}

UI_COLOURS = {
    'default': '#222222',
    'highlight': '#FFD700',
}

BACKGROUND_ASSET_DIR = 'assets/Backgrounds'
BACKCARD_ASSET_DIR = 'assets/CardBacks'

IN_DEBUG_MODE = True
IN_PROFILING_MODE = False  # Flag to enable/disable profiling

AUTHORS = [
    {'name': 'Valley of Delight',
     'artist': 'Caio Calazans',
     'file': 'assets/GameBoards/Valley of Delight.png'},
    {'name': 'Battlefield',
     'artist': 'Dan Seagrave',
     'file': 'assets/GameBoards/Battlefield.png'},
    {'name': 'Arid Desert',
     'artist': 'AronjaArt',
     'file': 'assets/GameBoards/Arid Desert.png'},
    {'name': 'Dragon Lord',
     'artist': 'Ed Beard Jr.',
     'file': 'assets/GameBoards/Dragonlord.png'},
    {'name': 'River of Flame',
     'artist': 'lan Miller',
     'file': 'assets/GameBoards/River of Flame.png'},
    {'name': 'Stream',
     'artist': 'Caio Calazans',
     'file': 'assets/GameBoards/Stream.png'},
    {'name': 'Lookout',
     'artist': 'Ossi Hiekkala',
     'file': 'assets/GameBoards/Lookout.png'},
    {'name': 'Planar Gate',
     'artist': 'Liz Danforth',
     'file': 'assets/GameBoards/Planar Gate.png'},
    {'name': 'Mirror Realm',
     'artist': 'Liz Danforth',
     'file': 'assets/GameBoards/Mirror Realm.png'},
]