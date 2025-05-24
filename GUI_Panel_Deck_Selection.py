import pygame
import Util_Effects
import Util_Config as config
from GUI_Panel import Panel
from typing import Dict, List, Optional
import Curiosa_Decks

class pDeck_Selection(Panel):
    # Effect settings
    EFFECT_SETTINGS = {
        'panel_slide': {
            'start_pos': (0, 0),
            'end_pos': (0, 0),
            'duration': 0.8
        },
        'button_pulse': {
            'scale_factor': 0.1,  # 10% scale
            'speed': 2.0  # Faster pulse
        }
    }
    
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self.showing = False
        self.current_category = None
        self.deck_hover_index = -1
        self.deck_hover_effect = None
        self.selected_deck = None
        
        # Initialize deck categories
        self.deck_categories = {
            'Standard': [
                'https://curiosa.io/deck/standard-1',
                'https://curiosa.io/deck/standard-2'
            ],
            'Limited': [
                'https://curiosa.io/deck/limited-1',
                'https://curiosa.io/deck/limited-2'
            ],
            'Custom': [
                'https://curiosa.io/deck/custom-1',
                'https://curiosa.io/deck/custom-2'
            ]
        }
        
        # Initialize effects
        self.panel_slide = None
        self.category_buttons = {}
        self.initialize_effects()
        
    def initialize_effects(self) -> None:
        """Initialize all panel effects."""
        window_height = self.screen.get_height()
        
        # Initialize panel slide effect
        self.panel_slide = Util_Effects.slide(
            start_pos=(0, window_height),
            end_pos=(0, int(window_height * 0.05)),
            duration=self.EFFECT_SETTINGS['panel_slide']['duration']
        )
        
        # Initialize category buttons
        for category in self.deck_categories.keys():
            self.category_buttons[category] = {
                'hover': False,
                'pulse': None  # Will be initialized when drawing
            }
            
    def show(self) -> None:
        """Show the panel with animation."""
        self.showing = True
        self.panel_slide.reset()
        
    def hide(self) -> None:
        """Hide the panel."""
        self.showing = False
        self.current_category = None
        self.deck_hover_index = -1
        self.deck_hover_effect = None
        self.selected_deck = None
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle panel events."""
        if not self.showing:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.handle_click(event)
        elif event.type == pygame.MOUSEMOTION:
            return self.handle_motion(event)
            
        return False
        
    def handle_click(self, event: pygame.event.Event) -> bool:
        """Handle mouse clicks in the panel."""
        mouse_x, mouse_y = event.pos
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate selection window dimensions
        selection_width = int(window_width * 0.9)
        selection_x = (window_width - selection_width) // 2
        selection_y = int(window_height * 0.05)
        
        # Handle category buttons
        if self.handle_category_click(mouse_x, mouse_y, selection_x, selection_y):
            return True
            
        # Handle deck selection
        self.handle_deck_click(mouse_x, mouse_y, selection_x, selection_y, selection_width)
        return True
        
    def handle_motion(self, event: pygame.event.Event) -> bool:
        """Handle mouse motion in the panel."""
        mouse_x, mouse_y = event.pos
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate selection window dimensions
        selection_width = int(window_width * 0.9)
        selection_x = (window_width - selection_width) // 2
        selection_y = int(window_height * 0.05)
        
        # Update category button hover states
        category_padding = 20
        category_width = 200
        category_height = 40
        category_y = selection_y + 80
        
        for i, category in enumerate(self.deck_categories.keys()):
            category_x = selection_x + category_padding + i * (category_width + category_padding)
            category_rect = pygame.Rect(category_x, category_y, category_width, category_height)
            
            was_hover = self.category_buttons[category]['hover']
            self.category_buttons[category]['hover'] = category_rect.collidepoint(mouse_x, mouse_y)
            
            # Reset pulse effect if hover state changed
            if was_hover != self.category_buttons[category]['hover']:
                if self.category_buttons[category]['pulse']:
                    self.category_buttons[category]['pulse'].reset()
                    
        return True
        
    def handle_category_click(self, mouse_x: int, mouse_y: int, selection_x: int, selection_y: int) -> bool:
        """Handle clicks on category buttons."""
        category_padding = 20
        category_width = 200
        category_height = 40
        category_y = selection_y + 80
        
        for i, category in enumerate(self.deck_categories.keys()):
            category_x = selection_x + category_padding + i * (category_width + category_padding)
            category_rect = pygame.Rect(category_x, category_y, category_width, category_height)
            if category_rect.collidepoint(mouse_x, mouse_y):
                self.current_category = category
                self.deck_hover_index = -1
                self.deck_hover_effect = None
                return True
        return False
        
    def handle_deck_click(self, mouse_x: int, mouse_y: int, selection_x: int, selection_y: int, selection_width: int) -> None:
        """Handle clicks on deck thumbnails."""
        if not self.current_category:
            return
            
        padding = 30
        thumbnails_per_row = 3
        thumb_width = (selection_width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
        thumb_height = int(thumb_width * 1.4)
        
        category_y = selection_y + 80
        category_height = 40
        
        decks = self.deck_categories[self.current_category]
        for i, deck_url in enumerate(decks):
            row = i // thumbnails_per_row
            col = i % thumbnails_per_row
            x = selection_x + padding + col * (thumb_width + padding)
            y = category_y + category_height + 40 + row * (thumb_height + padding + 40)
            rect = pygame.Rect(x, y, thumb_width, thumb_height)
            if rect.collidepoint(mouse_x, mouse_y):
                self.selected_deck = deck_url
                try:
                    deck_data = Curiosa_Decks.get_deck_json_from_curiosa(deck_url)
                    # TODO: Pass deck_data to Game_Manager to create the actual deck
                    self.hide()
                except Exception as e:
                    print(f"Error loading deck: {e}")
                    # TODO: Show error message to user
                break
                
    def update(self) -> None:
        """Update panel state and effects."""
        if not self.showing:
            return
            
        # Update panel slide effect
        self.panel_slide.update()
        
        # Update category button pulse effects
        for category in self.category_buttons.values():
            if category['hover'] and category['pulse']:
                category['pulse'].update()
                
    def draw(self) -> None:
        """Draw the panel."""
        if not self.showing:
            return
            
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate selection window dimensions
        selection_width = int(window_width * 0.9)
        selection_x = (window_width - selection_width) // 2
        selection_y = int(window_height * 0.05)
        
        # Draw semi-transparent background
        overlay = pygame.Surface((window_width, window_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw selection window
        selection_rect = pygame.Rect(selection_x, selection_y, selection_width, window_height - selection_y * 2)
        pygame.draw.rect(self.screen, (40, 40, 40), selection_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), selection_rect, 2)
        
        # Draw category buttons
        category_padding = 20
        category_width = 200
        category_height = 40
        category_y = selection_y + 80
        
        for i, category in enumerate(self.deck_categories.keys()):
            category_x = selection_x + category_padding + i * (category_width + category_padding)
            category_rect = pygame.Rect(category_x, category_y, category_width, category_height)
            
            # Draw button background
            pygame.draw.rect(self.screen, (60, 60, 60), category_rect)
            if self.category_buttons[category]['hover']:
                pygame.draw.rect(self.screen, (100, 100, 100), category_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), category_rect, 2)
            
            # Draw category text
            text = config.FONTS['text'].render(category, True, (200, 200, 200))
            text_rect = text.get_rect(center=category_rect.center)
            self.screen.blit(text, text_rect)
            
        # Draw decks if category is selected
        if self.current_category:
            self.draw_decks(selection_x, selection_y, selection_width)
            
    def draw_decks(self, selection_x: int, selection_y: int, selection_width: int) -> None:
        """Draw deck thumbnails for the selected category."""
        padding = 30
        thumbnails_per_row = 3
        thumb_width = (selection_width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
        thumb_height = int(thumb_width * 1.4)
        
        category_y = selection_y + 80
        category_height = 40
        
        decks = self.deck_categories[self.current_category]
        for i, deck_url in enumerate(decks):
            row = i // thumbnails_per_row
            col = i % thumbnails_per_row
            x = selection_x + padding + col * (thumb_width + padding)
            y = category_y + category_height + 40 + row * (thumb_height + padding + 40)
            rect = pygame.Rect(x, y, thumb_width, thumb_height)
            
            # Draw deck thumbnail
            pygame.draw.rect(self.screen, (60, 60, 60), rect)
            if i == self.deck_hover_index:
                pygame.draw.rect(self.screen, (100, 100, 100), rect)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
            
            # Draw deck name
            deck_name = f"Deck {i + 1}"
            text = config.FONTS['text'].render(deck_name, True, (200, 200, 200))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect) 