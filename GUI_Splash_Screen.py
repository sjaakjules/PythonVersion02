'''
Purpose: Display the game's splash screen with animated title and click handling.
Responsibilities:
    • Display the game title with animation effects
    • Handle mouse click to proceed to the main menu
    • Provide smooth transitions between screens
'''

import pygame
import Util_Effect_Factory
from typing import Optional, Tuple, Callable


class SplashScreen:
    def __init__(self, screen_size: Tuple[int, int], on_complete: Callable[[], None]) -> None:
        """
        Initialize the splash screen.
        
        Args:
            screen_size: Tuple of (width, height) for the screen
            on_complete: Callback function to execute when splash screen is complete
        """
        self.screen_size = screen_size
        self.on_complete = on_complete
        
        # Load title image
        self.title_image = pygame.image.load('assets/Icons/Sorcery Title.png').convert_alpha()
        self.title_rect = self.title_image.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2))
        
        # Create subtitle text
        self.subtitle_font = pygame.font.Font(None, 36)
        self.subtitle_text = self.subtitle_font.render("Click to continue", True, (200, 200, 200))
        self.subtitle_rect = self.subtitle_text.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2 + 100))
        
        # Create effects
        self.title_effect = Util_Effect_Factory.create_effect_from_config({
            'type': 'pulse',
            'settings': {
                'scale_factor': 0.1,
                'speed': 1.0,
                'loop': True
            }
        }, size=self.title_rect.size)
        
        self.subtitle_effect = Util_Effect_Factory.create_effect_from_config({
            'type': 'fade',
            'settings': {
                'start_alpha': 0,
                'end_alpha': 255,
                'duration': 1.0,
                'loop': True
            }
        })
        
        # State
        self.is_complete = False
        self.fade_out_effect: Optional[Util_Effect_Factory.fade] = None
        
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
            self.fade_out_effect = Util_Effect_Factory.create_effect_from_config({
                'type': 'fade',
                'settings': {
                    'start_alpha': 255,
                    'end_alpha': 0,
                    'duration': 0.5,
                    'loop': False
                }
            })
            
    def update(self) -> None:
        """Update the splash screen state."""
        if self.fade_out_effect is not None:
            self.fade_out_effect.update()
            if self.fade_out_effect.is_complete:
                self.is_complete = True
                self.on_complete()
            return
            
        # Update effects
        self.title_effect.update()
        self.subtitle_effect.update()
        
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the splash screen.
        
        Args:
            surface: The pygame surface to draw on
        """
        # Draw background
        surface.fill((0, 0, 0))
        
        if self.fade_out_effect is not None:
            # Apply fade out effect
            alpha = self.fade_out_effect.get_state()
            surface.set_alpha(alpha)
        else:
            # Get title effect state
            title_size, title_offset = self.title_effect.get_state()
            
            # Scale and position title image
            scaled_title = pygame.transform.scale(self.title_image, title_size)
            title_pos = (
                self.title_rect.centerx - title_size[0] // 2 + title_offset[0],
                self.title_rect.centery - title_size[1] // 2 + title_offset[1]
            )
            surface.blit(scaled_title, title_pos)
            
            # Get subtitle effect state
            subtitle_alpha = self.subtitle_effect.get_state()
            
            # Draw subtitle with fade effect
            subtitle_surface = self.subtitle_text.copy()
            subtitle_surface.set_alpha(subtitle_alpha)
            surface.blit(subtitle_surface, self.subtitle_rect) 