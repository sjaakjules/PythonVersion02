import pygame
from GUI_Panel import Panel
import Util_Config as config
import Util_Effects as effects


class BoardSelectionPanel(Panel):
    """Panel for selecting the game board."""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.hover_index = -1
        self.hover_effect = None
        self.thumbnail_cache = {}
        self.background_image = pygame.image.load('assets/Icons/Sorcery_Screen.png').convert()
        self.background_rect = self.background_image.get_rect()
        self.zoom_scale = 1.0
        self.zoom_speed = 0.02
        self.zoom_direction = 1
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        if not self.is_visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if self.is_point_in_panel(mouse_x, mouse_y):
                # Calculate thumbnail dimensions
                padding = 30
                thumbnails_per_row = 5
                thumb_width = (self.width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
                thumb_height = int(thumb_width * 0.7)
                
                # Check which thumbnail was clicked
                for i, board in enumerate(config.AUTHORS):
                    row = i // thumbnails_per_row
                    col = i % thumbnails_per_row
                    x = padding + col * (thumb_width + padding)
                    y = (self.height * 0.3 if row == 0 else self.height * 0.6)
                    rect = pygame.Rect(x, y, thumb_width, thumb_height)
                    if rect.collidepoint(mouse_x - self.x, mouse_y - self.y):
                        return True  # Signal that a board was selected
                return False
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            if self.is_point_in_panel(mouse_x, mouse_y):
                # Calculate thumbnail dimensions
                padding = 30
                thumbnails_per_row = 5
                thumb_width = (self.width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
                thumb_height = int(thumb_width * 0.7)
                
                # Update hover state
                for i, board in enumerate(config.AUTHORS):
                    row = i // thumbnails_per_row
                    col = i % thumbnails_per_row
                    x = padding + col * (thumb_width + padding)
                    y = (self.height * 0.3 if row == 0 else self.height * 0.6)
                    rect = pygame.Rect(x, y, thumb_width, thumb_height)
                    if rect.collidepoint(mouse_x - self.x, mouse_y - self.y):
                        if self.hover_index != i:
                            self.hover_index = i
                            self.hover_effect = effects.pulse((thumb_width, thumb_height), scale_factor=0.05)
                        return True
                else:
                    if self.hover_index != -1:
                        self.hover_index = -1
                        self.hover_effect = None
                return True
        return False
        
    def update(self) -> None:
        """Update panel state and effects."""
        super().update()
        if self.hover_effect:
            self.hover_effect.update()
            
        # Update zoom effect
        self.zoom_scale = 1.0 + (self.zoom_speed * self.zoom_direction)
        if self.zoom_scale >= 1.1 or self.zoom_scale <= 0.9:
            self.zoom_direction *= -1
            
    def draw_content(self) -> None:
        """Draw the panel's content."""
        # Draw title
        title = config.FONTS['title'].render("Select Game Board", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.width // 2, centery=30)
        self.surface.blit(title, title_rect)
        
        # Calculate layout for thumbnails
        padding = 30
        thumbnails_per_row = 5
        thumb_width = (self.width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
        thumb_height = int(thumb_width * 0.7)
        
        # Draw thumbnails
        for i, board in enumerate(config.AUTHORS):
            row = i // thumbnails_per_row
            col = i % thumbnails_per_row
            x = padding + col * (thumb_width + padding)
            y = (self.height * 0.3 if row == 0 else self.height * 0.6)
            
            # Get or create thumbnail
            board_file = board['file']
            if board_file not in self.thumbnail_cache:
                thumbnail = pygame.image.load(board_file).convert_alpha()
                thumbnail = pygame.transform.scale(thumbnail, (thumb_width, thumb_height))
                self.thumbnail_cache[board_file] = thumbnail
            else:
                thumbnail = self.thumbnail_cache[board_file]
            
            # Apply hover effect if this is the hovered thumbnail
            if i == self.hover_index and self.hover_effect:
                scaled_size, offset = self.hover_effect.get_state()
                scaled_thumbnail = pygame.transform.scale(thumbnail, scaled_size)
                self.surface.blit(scaled_thumbnail, (x - offset[0], y - offset[1]))
            else:
                self.surface.blit(thumbnail, (x, y))
            
            # Draw artist credit
            credit_text = config.FONTS['subtle'].render(board['artist'], True, (200, 200, 200))
            credit_rect = credit_text.get_rect(centerx=x + thumb_width // 2, top=y + thumb_height + 5)
            self.surface.blit(credit_text, credit_rect)
            
    def is_point_in_panel(self, x: int, y: int) -> bool:
        """Check if a point is within the panel's bounds."""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height) 