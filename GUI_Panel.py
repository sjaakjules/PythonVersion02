import pygame
import Util_Effects as effects
import Util_Config as config


class Panel:
    """Base class for all UI panels/windows."""
    
    def __init__(self, screen: pygame.Surface, width: float = 0.9, height: float = 0.9):
        """
        Initialize a panel.
        
        Args:
            screen: The pygame surface to draw on
            width: Width as percentage of screen width (0.0-1.0)
            height: Height as percentage of screen height (0.0-1.0)
        """
        self.screen = screen
        self.width_ratio = width
        self.height_ratio = height
        self.entrance_effect = None
        self.exit_effect = None
        self.is_visible = False
        self.is_exiting = False
        self.surface = None
        self.update_surface()
        
    def update_surface(self) -> None:
        """Update the panel surface size based on screen dimensions."""
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate panel dimensions
        self.width = int(window_width * self.width_ratio)
        self.height = int(window_height * self.height_ratio)
        self.x = (window_width - self.width) // 2
        self.y = int(window_height * 0.05)  # Default to 5% from top
        
        # Create new surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
    def show(self) -> None:
        """Show the panel with entrance effect."""
        self.is_visible = True
        self.is_exiting = False
        window_height = self.screen.get_height()
        self.entrance_effect = effects.slide(
            start_pos=(0, window_height),
            end_pos=(0, int(window_height * 0.05)),
            duration=0.8
        )
        
    def hide(self) -> None:
        """Hide the panel with exit effect."""
        if not self.is_visible:
            return
            
        self.is_exiting = True
        self.exit_effect = effects.fade(
            start_alpha=255,
            end_alpha=0,
            duration=0.3
        )
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        return False
        
    def update(self) -> None:
        """Update panel state and effects."""
        if self.entrance_effect:
            self.entrance_effect.update()
            if self.entrance_effect.is_complete:
                self.entrance_effect = None
                
        if self.exit_effect:
            self.exit_effect.update()
            if self.exit_effect.is_complete:
                self.is_visible = False
                self.is_exiting = False
                self.exit_effect = None
            
    def draw(self) -> None:
        """Draw the panel."""
        if not self.is_visible and not self.is_exiting:
            return
            
        # Clear the surface
        self.surface.fill((0, 0, 0, 200))  # Semi-transparent black
        
        # Draw border
        self.draw_border()
        
        # Draw content (to be implemented by subclasses)
        self.draw_content()
        
        # Apply effects
        if self.entrance_effect:
            current_pos, _ = self.entrance_effect.get_state()
            self.screen.blit(self.surface, (self.x, current_pos[1]))
        elif self.exit_effect:
            alpha = self.exit_effect.get_state()
            temp_surface = self.surface.copy()
            temp_surface.set_alpha(alpha)
            self.screen.blit(temp_surface, (self.x, self.y))
        else:
            self.screen.blit(self.surface, (self.x, self.y))
            
    def draw_border(self) -> None:
        """Draw the panel's border with 3D effect."""
        border_width = 4
        base_gold = (170, 149, 96)
        
        # Create highlight and shadow colors
        highlight_gold = (int(base_gold[0] * 1.2), int(base_gold[1] * 1.2), int(base_gold[2] * 1.2))
        shadow_gold = (int(base_gold[0] * 0.8), int(base_gold[1] * 0.8), int(base_gold[2] * 0.8))
        
        # Draw border lines
        pygame.draw.line(self.surface, highlight_gold, (0, 0), (self.width, 0), border_width // 2)
        pygame.draw.line(self.surface, shadow_gold, (0, border_width // 2), 
                        (self.width, border_width // 2), border_width // 2)
        
        pygame.draw.line(self.surface, highlight_gold, (0, 0), (0, self.height), border_width // 2)
        pygame.draw.line(self.surface, shadow_gold, (border_width // 2, 0), 
                        (border_width // 2, self.height), border_width // 2)
        
        pygame.draw.line(self.surface, shadow_gold, (0, self.height - border_width), 
                        (self.width, self.height - border_width), border_width // 2)
        pygame.draw.line(self.surface, highlight_gold, (0, self.height - border_width // 2), 
                        (self.width, self.height - border_width // 2), border_width // 2)
        
        pygame.draw.line(self.surface, shadow_gold, (self.width - border_width, 0), 
                        (self.width - border_width, self.height), border_width // 2)
        pygame.draw.line(self.surface, highlight_gold, (self.width - border_width // 2, 0), 
                        (self.width - border_width // 2, self.height), border_width // 2)
        
    def draw_content(self) -> None:
        """Draw the panel's content. To be implemented by subclasses."""
        pass 