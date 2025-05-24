import pygame
import Util_Config as config
from Util_Effect_Factory import EffectFactory
from typing import Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from GUI_Manager import GUI_Manager

from GUI_Panel import Panel
from GUI_Panel_Board_Selection import pBoard_Selection
from GUI_Panel_Deck_Selection import pDeck_Selection


class Main_Window:
    # Effect settings
    EFFECT_SETTINGS = {
        'button_effect': {
            'type': 'pulse',
            'settings': {
                'scale_factor': 0.1,  # 10% scale
                'speed': 2.0  # Faster pulse
            }
        }
    }
    
    def __init__(self, screen: pygame.Surface, ui: 'GUI_Manager') -> None:
        self.screen = screen
        self.ui = ui
        
        # Preload background image and cache it
        self.background_image = pygame.image.load('assets/Icons/Sorcery_Screen.png').convert()
        self.background_rect = self.background_image.get_rect()
        
        # Pre-calculate scaled background for different window sizes
        self.scaled_backgrounds = {}
        self.update_scaled_backgrounds()
        
        # Menu state
        self.showing_menu = True
        self.clicked_button = None  # Track which button was clicked
        self.menu_buttons = {
            'add_board': {
                'image': pygame.image.load('assets/Misc/Add Gameboard AI_gen.png').convert_alpha(),
                'rect': None,
                'hover': False,
                'pulse': None  # Will be initialized after image is loaded
            },
            'add_deck_p1': {
                'image': pygame.image.load('assets/Misc/Add Deck AI_gen.png').convert_alpha(),
                'rect': None,
                'hover': False,
                'pulse': None  # Will be initialized after image is loaded
            },
            'add_deck_p2': {
                'image': pygame.image.load('assets/Misc/Add Deck AI_gen.png').convert_alpha(),
                'rect': None,
                'hover': False,
                'pulse': None  # Will be initialized after image is loaded
            }
        }
        
        # Initialize panels
        self.panels: Dict[str, Panel] = {}
        self.active_panel: Optional[Panel] = None
        self.board_panel = pBoard_Selection(self.screen)
        self.deck_panel = pDeck_Selection(self.screen)
        self.board_panel.hide()  # Hide the board selection panel by default
        self.deck_panel.hide()   # Hide the deck selection panel by default
        
        # Update button positions and initialize pulse effects
        self.update_menu_button_positions()
            
    def update(self) -> None:
        """Update window effects."""
        # Update active panel
        if self.active_panel:
            self.active_panel.update()
            
        # Update pulse effects for menu buttons
        if self.showing_menu:
            for button in self.menu_buttons.values():
                if button['hover']:
                    button['pulse'].update()
            
    def draw(self) -> None:
        """Draw the main window with all its elements."""
        # Fill with black
        self.screen.fill((0, 0, 0))
        
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Get pre-scaled background
        scaled_bg = self.get_scaled_background(window_width, window_height)
            
        # Center the background
        bg_x = (window_width - scaled_bg.get_width()) // 2
        bg_y = (window_height - scaled_bg.get_height()) // 2
        
        # Draw the background
        self.screen.blit(scaled_bg, (bg_x, bg_y))
                
        # Draw menu if active
        if self.showing_menu:
            self.draw_menu()
            
        # Draw active panel if it exists
        if self.active_panel:
            self.active_panel.draw()
            
    def update_menu_button_positions(self) -> None:
        """Update the positions of menu buttons based on screen size."""
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate button sizes
        board_height = window_height // 5  # 1/5th of screen height for board button
        deck_height = window_height // 10  # Keep deck buttons at 1/10th
        
        # Center positions
        center_x = window_width // 2
        center_y = window_height // 2
        
        # Scale board button image
        board_img = self.menu_buttons['add_board']['image']
        aspect_ratio = board_img.get_width() / board_img.get_height()
        new_width = int(board_height * aspect_ratio)
        self.menu_buttons['add_board']['image'] = pygame.transform.scale(board_img, (new_width, board_height))
        
        # Initialize board button pulse effect with the scaled size
        self.menu_buttons['add_board']['pulse'] = EffectFactory.create_effect_from_config(
            self.EFFECT_SETTINGS['button_effect'],
            size=(new_width, board_height)
        )
        
        # Scale deck button images
        for button_id in ['add_deck_p1', 'add_deck_p2']:
            img = self.menu_buttons[button_id]['image']
            aspect_ratio = img.get_width() / img.get_height()
            new_width = int(deck_height * aspect_ratio)
            self.menu_buttons[button_id]['image'] = pygame.transform.scale(img, (new_width, deck_height))
            
            # Initialize deck button pulse effect with the scaled size
            self.menu_buttons[button_id]['pulse'] = EffectFactory.create_effect_from_config(
                self.EFFECT_SETTINGS['button_effect'],
                size=(new_width, deck_height)
            )
        
        # Board button (top)
        board_img = self.menu_buttons['add_board']['image']
        board_rect = board_img.get_rect(center=(center_x, center_y - 100))
        self.menu_buttons['add_board']['rect'] = board_rect
        
        # Deck buttons (bottom)
        deck_img = self.menu_buttons['add_deck_p1']['image']
        deck_rect1 = deck_img.get_rect(center=(center_x - 100, center_y + 100))
        deck_rect2 = deck_img.get_rect(center=(center_x + 100, center_y + 100))
        self.menu_buttons['add_deck_p1']['rect'] = deck_rect1
        self.menu_buttons['add_deck_p2']['rect'] = deck_rect2
        
    def draw_menu(self) -> None:
        """Draw the main menu with buttons."""
        if not self.showing_menu:
            return
            
        # Draw buttons
        for button_id, button in self.menu_buttons.items():
            if button['hover']:
                # Get pulse effect state
                scaled_size, offset = button['pulse'].get_state()
                # Scale image based on pulse effect
                img = button['image']
                scaled_img = pygame.transform.scale(img, scaled_size)
                # Calculate position to maintain center
                pos_x = button['rect'].centerx - scaled_size[0] // 2
                pos_y = button['rect'].centery - scaled_size[1] // 2
                self.screen.blit(scaled_img, (pos_x, pos_y))
            else:
                self.screen.blit(button['image'], button['rect'])
                
    def handle_menu_click(self, event: pygame.event.Event) -> tuple[bool, str | None]:
        """Handle menu button clicks and return True if a panel should be shown."""
        if not self.showing_menu:
            return False, None
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for button_id, button in self.menu_buttons.items():
                if button['rect'].collidepoint(mouse_x, mouse_y):
                    self.clicked_button = button_id
                    self.showing_menu = False
                    if button_id == 'add_board':
                        return True, 'board'
                    elif button_id in ['add_deck_p1', 'add_deck_p2']:
                        return True, 'deck'
        return False, None
        
    def handle_menu_motion(self, event: pygame.event.Event) -> bool:
        """Handle mouse motion over menu buttons."""
        if not self.showing_menu:
            return False
            
        mouse_x, mouse_y = event.pos
        
        # Update hover state for each button
        for button in self.menu_buttons.values():
            was_hover = button['hover']
            button['hover'] = button['rect'].collidepoint(mouse_x, mouse_y)
            
            # Reset pulse effect if hover state changed
            if was_hover != button['hover']:
                button['pulse'].reset()
            
        return True
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        # Handle menu interactions
        if self.showing_menu:
            if self.handle_menu_motion(event):
                return True
            if self.handle_menu_click(event)[0]:
                return True
                
        # Handle panel interactions
        if self.active_panel:
            return self.active_panel.handle_event(event)
            
        return False
        
    def show_panel(self, panel_type: str) -> None:
        """Show a specific panel."""
        if panel_type == 'board':
            self.active_panel = self.board_panel
            self.board_panel.show()
        elif panel_type == 'deck':
            self.active_panel = self.deck_panel
            self.deck_panel.show()
            
    def hide_panel(self, panel_type: str) -> None:
        """Hide a specific panel."""
        if panel_type == 'board':
            self.board_panel.hide()
        elif panel_type == 'deck':
            self.deck_panel.hide()
        self.active_panel = None
        self.showing_menu = True
        
    def get_active_panel(self) -> Panel | None:
        """Get the currently active panel."""
        return self.active_panel
        
    def get_scaled_background(self, window_width: int, window_height: int) -> pygame.Surface:
        """Get a scaled background image for the current window size."""
        # Create a key for the current size
        size_key = (window_width, window_height)
        
        # Return cached version if available
        if size_key in self.scaled_backgrounds:
            return self.scaled_backgrounds[size_key]
            
        # Calculate scale to fit window while maintaining aspect ratio
        bg_width, bg_height = self.background_image.get_size()
        scale = min(window_width / bg_width, window_height / bg_height)
        
        # Create scaled version
        new_width = int(bg_width * scale)
        new_height = int(bg_height * scale)
        scaled_bg = pygame.transform.smoothscale(self.background_image, (new_width, new_height))
        
        # Cache the result
        self.scaled_backgrounds[size_key] = scaled_bg
        
        return scaled_bg
        
    def update_scaled_backgrounds(self) -> None:
        """Update the cache of scaled backgrounds."""
        self.scaled_backgrounds.clear()
        # Pre-calculate some common sizes
        common_sizes = [
            (1920, 1080),  # Full HD
            (1280, 720),   # HD
            (800, 600)     # Common window size
        ]
        for width, height in common_sizes:
            self.get_scaled_background(width, height) 