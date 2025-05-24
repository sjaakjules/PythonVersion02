'''
Purpose: Display the game's splash screen with animated title and click handling.
Responsibilities:
    • Display the game title with animation effects
    • Handle mouse click to proceed to the main menu
    • Provide smooth transitions between screens
'''

import pygame
from Util_Effect_Factory import EffectFactory as effects
from typing import Optional, Tuple, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from GUI_Manager import GUI_Manager


class Splash_Screen:
    
    SPLASH_SCREEN_EFFECTS = {
        'in': {
            'type': 'fade',
            'settings': {
                'start_alpha': 0,
                'end_alpha': 255,
                'duration': 1.0,
                'loop': False
            }
        }, 'out': {
            'type': 'fade',
            'settings': {
                'start_alpha': 255,
                'end_alpha': 0,
                'duration': 0.5,
                'loop': False
            }
        }, 'subtitle': {
            'type': 'pulse',
            'settings': {
                'scale_factor': 0.2,
                'speed': 4.0,
                'loop': True
            }
        },
    }
    
    def __init__(self, screen: pygame.Surface, ui: 'GUI_Manager') -> None:
        """
        Initialize the splash screen.
        
        Args:
            screen: The pygame surface to draw on
            ui: The GUI manager instance
        """
        # State
        self.is_complete = False
        
        self.screen = screen
        self.screen_size = (screen.get_width(), screen.get_height())
        self.initial_screen_size = self.screen_size
        self.screen_scale = 1.0
        self.ui = ui
        
        # Load title image
        self.title_image = pygame.image.load('assets/Icons/Sorcery Title.png').convert_alpha()
        self.title_rect = self.title_image.get_rect(center=(self.screen_size[0] // 2, self.screen_size[1] // 2))
        
        # Create subtitle text - render at 2x size for better quality when scaling
        self.subtitle_font = pygame.font.Font(None, 72)  # 2x the original size
        self.subtitle_text = self.subtitle_font.render("Click to Start", True, (200, 200, 200))
        self.offset_ratio = 3
        self.subtitle_rect = self.subtitle_text.get_rect(center=(self.screen_size[0] // 2,
                                                                 self.screen_size[1] // 2 + self.screen.get_height() // self.offset_ratio))
        
        # Create effects
        self.fade_in_effect = effects.create_effect_from_config(
            self.SPLASH_SCREEN_EFFECTS['in'])
        
        self.fade_out_effect: Optional[effects.fade] = None
        
        self.subtitle_effect = effects.create_effect_from_config(
            self.SPLASH_SCREEN_EFFECTS['subtitle'], size=self.subtitle_rect.size)
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        if self.is_complete or self.fade_out_effect is not None:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Start fade out
            self.fade_out_effect = effects.create_effect_from_config(
                self.SPLASH_SCREEN_EFFECTS['out'])
            
    def update(self) -> bool:
        """
        Update the splash screen state.
        
        Returns:
            bool: True when the splash screen is still active, False when complete
        """
        if not self.is_complete:
            
            current_size = (self.screen.get_width(), self.screen.get_height())
            if current_size != self.screen_size:
                self.screen_size = current_size
                # Scale title image proportionally
                self.screen_scale = min(self.screen_size[0] / self.initial_screen_size[0], self.screen_size[1] / self.initial_screen_size[1])
                
            if self.fade_out_effect is not None:
                self.fade_out_effect.update()
                if self.fade_out_effect.is_complete:
                    self.is_complete = True
                    self.ui.unsubscribe_from_event(pygame.MOUSEBUTTONDOWN, self.handle_event)
                    return False
                
            # Update effects
            self.fade_in_effect.update()
            self.subtitle_effect.update()
        else:
            return False
        return True
    
    def draw(self) -> bool:
        """
        Draw the splash screen.
        
        Returns:
            bool: True when the splash screen is still active, False when complete
        """
        if not self.is_complete:
            # Check for screen size changes
            current_size = (self.screen.get_width(), self.screen.get_height())
            if current_size != self.screen_size:
                self.screen_size = current_size
                # Calculate scale factor based on initial size
                self.screen_scale = min(self.screen_size[0] / self.initial_screen_size[0], 
                                      self.screen_size[1] / self.initial_screen_size[1])
            
            # Draw background as metal grey
            self.screen.fill((56, 56, 60))
            
            if self.fade_out_effect is not None:
                # Apply fade out effect
                alpha = self.fade_out_effect.get_state()
                self.screen.set_alpha(alpha)
            else:
                # Get title effect state
                alpha = self.fade_in_effect.get_state()
                
                # Scale and position title image
                scaled_title_size = (int(self.title_image.get_width() * self.screen_scale), 
                                   int(self.title_image.get_height() * self.screen_scale))
                self.scaled_title = pygame.transform.smoothscale(self.title_image, scaled_title_size)
                self.title_rect = self.scaled_title.get_rect(center=(self.screen_size[0] // 2, 
                                                                   self.screen_size[1] // 2))
                self.screen.blit(self.scaled_title, self.title_rect)
                self.screen.set_alpha(alpha)
                
                if self.fade_in_effect.is_complete:
                    # Update subtitle position
                    self.subtitle_rect = self.subtitle_text.get_rect(center=(self.screen_size[0] // 2,
                                                                           self.screen_size[1] // 2 + self.screen_size[1] // self.offset_ratio))
                    
                    # Get subtitle effect state
                    subtitle_size, subtitle_offset = self.subtitle_effect.get_state()
                    
                    # Scale the subtitle size by screen scale
                    scaled_subtitle_size = (int(subtitle_size[0] * self.screen_scale),
                                          int(subtitle_size[1] * self.screen_scale))
                    
                    # Scale the pre-rendered text
                    scaled_subtitle = pygame.transform.smoothscale(self.subtitle_text, scaled_subtitle_size)
                    
                    # Calculate center position for subtitle
                    center_x = self.screen_size[0] // 2
                    center_y = self.screen_size[1] // 2 + self.screen_size[1] // self.offset_ratio
                    
                    # Calculate position with offset from center
                    subtitle_x = center_x - scaled_subtitle_size[0] // 2
                    subtitle_y = center_y - scaled_subtitle_size[1] // 2
                    subtitle_pos = (subtitle_x, subtitle_y)
                    
                    self.screen.blit(scaled_subtitle, subtitle_pos)
                    
                    # Subscribe to mouse click event.
                    self.ui.subscribe_to_event(pygame.MOUSEBUTTONDOWN, self.handle_event)
            
            return True
        return False
    