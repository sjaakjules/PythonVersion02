'''
Purpose: Stores game-wide constants and styling presets.
Responsibilities:
	•	Player color themes (Red, Blue)
	•	Element color mapping (Air, Earth, Fire, Water)
	•	Font types, UI backgrounds
	•	inDebugMode toggle for development
'''

import pygame

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


FONTS = {
    'title': pygame.font.Font(None, 48),
    'subtitle': pygame.font.Font(None, 40),
    'selection': pygame.font.Font(None, 36),
    'debug': pygame.font.Font(None, 24),
}

UI_COLOURS = {
    'default': '#222222',
    'highlight': '#FFD700',
}

BACKGROUND_ASSET_DIR = 'assets/Backgrounds'
BACKCARD_ASSET_DIR = 'assets/CardBacks'

IN_DEBUG_MODE = True

