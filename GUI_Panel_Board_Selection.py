import pygame
from GUI_Panel import Panel
import Util_Config as config
import Util_Effects as effects
from Util_Debug import Debug_Display
import time

# Panel layout settings
PANEL_WIDTH_RATIO = 0.9
PANEL_HEIGHT_RATIO = 0.7
PADDING = 30  # Increased padding for better spacing
THUMBNAILS_PER_ROW = 3  # Changed to 3 thumbnails per row
THUMBNAIL_HEIGHT_RATIO = 0.7  # Height relative to width

# Effect settings
HOVER_SCALE_FACTOR = 0.05  # How much the thumbnail scales on hover
HOVER_SPEED = 5.0  # Speed of the hover animation
SCROLL_SPEED = 30  # Pixels per scroll wheel movement

# Animation settings
ANIMATION_SETTINGS = {
    'panel_slide_in': {
        'start_offset': 1000,  # Start off screen
        'end_offset': 0,       # End at normal position
        'duration': 0.5,       # 0.5 seconds
        'ease': 'cubic_out',   # Cubic ease-out
        'loop': False
    },
    'panel_slide_out': {
        'start_offset': 0,     # Start at normal position
        'end_offset': 1000,    # End off screen
        'duration': 0.3,       # 0.3 seconds
        'ease': 'cubic_in',    # Cubic ease-in
        'loop': False
    },
    'thumbnail_hover': {
        'start_scale': 1.0,
        'end_scale': 1.05,     # 5% larger
        'duration': 0.2,
        'ease': 'quad_out',
        'loop': True
    }
}

# Text colors
TITLE_COLOR = (255, 255, 255)
ARTIST_COLOR = (200, 200, 200)
SCROLLBAR_COLOR = (200, 200, 200, 128)

# Text positioning
NAME_Y_OFFSET = 0  # Center of thumbnail for name
ARTIST_Y_OFFSET = 5  # Distance below thumbnail for artist name

# Edge settings
EDGE_THICKNESS = 4
EDGE_COLOR = (212, 175, 55)  # Gold color
EDGE_SHADOW_COLOR = (100, 80, 20)  # Darker gold for shadow
EDGE_SHADOW_OFFSET = 2  # Pixels of shadow offset


class pBoard_Selection(Panel):
    """Panel for selecting the game board."""
    
    def __init__(self, screen: pygame.Surface):
        # Initialize debug display first
        self.debug_display = Debug_Display(screen, pygame.time.Clock())
        
        # Then call parent constructor
        super().__init__(screen, width=PANEL_WIDTH_RATIO, height=PANEL_HEIGHT_RATIO)
        
        # Initialize other attributes
        self.hover_index = -1
        self.hover_effect = None
        self.thumbnail_cache = {}
        self.background_image = pygame.image.load('assets/Icons/Sorcery_Screen.png').convert()
        self.background_rect = self.background_image.get_rect()
        self.scroll_offset = 0
        self.max_scroll = 0
        self.selected_board = None
        
        # Add drag scrolling state
        self.is_dragging = False
        self.drag_start_y = 0
        self.drag_start_offset = 0
        
        # Add animation state
        self.animation_state = {
            'current': None,
            'start_time': 0,
            'current_offset': 0
        }
        
    def show(self) -> None:
        """Show the panel with slide animation."""
        super().show()
        self.start_animation('panel_slide_in')
        
    def hide(self) -> None:
        """Hide the panel with slide animation."""
        self.start_animation('panel_slide_out')
        
    def start_animation(self, animation_name: str) -> None:
        """Start a new animation."""
        if animation_name in ANIMATION_SETTINGS:
            self.animation_state['current'] = animation_name
            self.animation_state['start_time'] = time.time()
            self.animation_state['current_offset'] = ANIMATION_SETTINGS[animation_name]['start_offset']
            self.debug_display.add_message(f"Starting animation: {animation_name}")
            
    def update_animation(self) -> None:
        """Update the current animation."""
        if not self.animation_state['current']:
            return
            
        settings = ANIMATION_SETTINGS[self.animation_state['current']]
        elapsed = time.time() - self.animation_state['start_time']
        progress = min(1.0, elapsed / settings['duration'])
        
        # Apply easing function
        if settings['ease'] == 'cubic_out':
            ease = 1 - (1 - progress) ** 3
        elif settings['ease'] == 'cubic_in':
            ease = progress ** 3
        elif settings['ease'] == 'quad_out':
            ease = 1 - (1 - progress) ** 2
        else:
            ease = progress
            
        # Calculate new offset
        distance = settings['end_offset'] - settings['start_offset']
        new_offset = settings['start_offset'] + (distance * ease)
        self.animation_state['current_offset'] = new_offset
        
        # Check if animation is complete
        if progress >= 1.0:
            if not settings['loop']:
                self.animation_state['current'] = None
            else:
                self.animation_state['start_time'] = time.time()
                
        self.debug_display.add_message(f"Animation: {self.animation_state['current']}, progress={progress:.2f}, offset={new_offset:.1f}")
        
    def handle_mouse_motion(self, event: pygame.event.Event) -> bool:
        """Handle mouse motion events."""
        if not self.is_visible:
            return False
            
        mouse_x, mouse_y = event.pos
        if self.is_point_in_panel(mouse_x, mouse_y):
            # Handle drag scrolling
            if self.is_dragging:
                delta_y = mouse_y - self.drag_start_y
                new_offset = self.drag_start_offset - delta_y
                self.scroll_offset = max(0, min(self.max_scroll, new_offset))
                self.debug_display.add_message(f"Drag Scroll: delta={delta_y}, new_offset={self.scroll_offset}")
                return True
            
            # Calculate thumbnail dimensions
            thumb_width = (self.width - (PADDING * (THUMBNAILS_PER_ROW + 1))) // THUMBNAILS_PER_ROW
            thumb_height = int(thumb_width * THUMBNAIL_HEIGHT_RATIO)
            
            # Update hover state
            found_hover = False
            for i, board in enumerate(config.AUTHORS):
                row = i // THUMBNAILS_PER_ROW
                col = i % THUMBNAILS_PER_ROW
                x = PADDING + col * (thumb_width + PADDING)
                y = PADDING + row * (thumb_height + PADDING + 60) - self.scroll_offset
                rect = pygame.Rect(x, y, thumb_width, thumb_height)
                if rect.collidepoint(mouse_x - self.x, mouse_y - self.y):
                    found_hover = True
                    if self.hover_index != i:
                        self.hover_index = i
                        # Create new hover effect
                        self.hover_effect = effects.pulse((thumb_width, thumb_height), 
                                                        scale_factor=HOVER_SCALE_FACTOR, 
                                                        speed=HOVER_SPEED)
                        self.debug_display.add_message(f"Hover: {board['name']} by {board['artist']}")
                    break
            
            if not found_hover and self.hover_index != -1:
                self.hover_index = -1
                self.hover_effect = None
                self.debug_display.add_message("Hover cleared")
            return True
        return False
        
    def handle_mouse_click(self, event: pygame.event.Event) -> bool:
        """Handle mouse click events."""
        if not self.is_visible:
            return False
            
        mouse_x, mouse_y = event.pos
        if self.is_point_in_panel(mouse_x, mouse_y):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                self.is_dragging = True
                self.drag_start_y = mouse_y
                self.drag_start_offset = self.scroll_offset
                self.debug_display.add_message(f"Drag Start: y={mouse_y}, offset={self.scroll_offset}")
                return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click release
                if self.is_dragging:
                    self.is_dragging = False
                    self.debug_display.add_message("Drag End")
                    return True
                
            # Only check for board selection if we're not dragging
            if not self.is_dragging:
                # Calculate thumbnail dimensions
                thumb_width = (self.width - (PADDING * (THUMBNAILS_PER_ROW + 1))) // THUMBNAILS_PER_ROW
                thumb_height = int(thumb_width * THUMBNAIL_HEIGHT_RATIO)
                
                # Check which thumbnail was clicked
                for i, board in enumerate(config.AUTHORS):
                    row = i // THUMBNAILS_PER_ROW
                    col = i % THUMBNAILS_PER_ROW
                    x = PADDING + col * (thumb_width + PADDING)
                    y = PADDING + row * (thumb_height + PADDING) - self.scroll_offset
                    rect = pygame.Rect(x, y, thumb_width, thumb_height)
                    if rect.collidepoint(mouse_x - self.x, mouse_y - self.y):
                        self.selected_board = board
                        return True  # Signal that a board was selected
            return True  # Return True to indicate we handled the click
        return False
        
    def handle_mouse_wheel(self, event: pygame.event.Event) -> bool:
        """Handle mouse wheel events."""
        if not self.is_visible:
            return False
            
        # Debug the event
        self.debug_display.add_message(f"Wheel Event: y={event.y}, precise={event.precise_y if hasattr(event, 'precise_y') else 'N/A'}")
        
        # Calculate new scroll offset
        new_offset = self.scroll_offset - event.y * SCROLL_SPEED
        self.debug_display.add_message(f"Scroll: current={self.scroll_offset}, new={new_offset}, max={self.max_scroll}")
        
        # Update scroll offset
        self.scroll_offset = max(0, min(self.max_scroll, new_offset))
        return True
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        if not self.is_visible:
            return False
            
        # Debug all events
        if config.IN_DEBUG_MODE:
            self.debug_display.add_message(f"Event: {pygame.event.event_name(event.type)}")
            
        if event.type == pygame.MOUSEMOTION:
            return self.handle_mouse_motion(event)
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return self.handle_mouse_click(event)
        elif event.type == pygame.MOUSEWHEEL:
            return self.handle_mouse_wheel(event)
        return False
        
    def update_surface(self) -> None:
        """Update the panel surface size based on screen dimensions."""
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate panel dimensions
        self.width = int(window_width * self.width_ratio)
        self.height = int(window_height * self.height_ratio)
        self.x = (window_width - self.width) // 2
        self.y = (window_height - self.height) // 2
        
        # Create new surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Calculate thumbnail dimensions
        thumb_width = (self.width - (PADDING * (THUMBNAILS_PER_ROW + 1))) // THUMBNAILS_PER_ROW
        thumb_height = int(thumb_width * THUMBNAIL_HEIGHT_RATIO)
        
        # Calculate total content height including text and padding
        rows = (len(config.AUTHORS) + THUMBNAILS_PER_ROW - 1) // THUMBNAILS_PER_ROW
        content_height = (thumb_height + PADDING + 60) * rows  # Added 60 for text space
        content_height += PADDING  # Add padding at bottom
        
        # Calculate maximum scroll
        self.max_scroll = max(0, content_height - (self.height - 60))  # Subtract title area height
        
        # Reset scroll if content fits
        if self.max_scroll == 0:
            self.scroll_offset = 0
            
        self.debug_display.add_message(f"Surface Update: max_scroll={self.max_scroll}, content_height={content_height}")
        
    def update(self) -> None:
        """Update panel state and effects."""
        super().update()
        if self.hover_effect:
            self.hover_effect.update()
            
        # Update animations
        self.update_animation()
        self.debug_display.update()
        
    def draw_content(self) -> None:
        """Draw the panel's content."""
        # Clear debug messages at start of frame
        self.debug_display.clear_messages()
        
        # Draw title
        title = config.FONTS['title'].render("Select Game Board", True, TITLE_COLOR)
        title_rect = title.get_rect(centerx=self.width // 2, centery=30)
        self.surface.blit(title, title_rect)
        
        # Calculate thumbnail dimensions
        thumb_width = (self.width - (PADDING * (THUMBNAILS_PER_ROW + 1))) // THUMBNAILS_PER_ROW
        thumb_height = int(thumb_width * THUMBNAIL_HEIGHT_RATIO)
        
        # Create a clipping rect for the content area
        content_rect = pygame.Rect(0, 60, self.width, self.height - 60)  # Start below title
        self.surface.set_clip(content_rect)
        
        # Get current mouse position relative to panel
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x -= self.x
        mouse_y -= self.y
        
        # Add mouse position to debug display
        self.debug_display.add_message(f"Mouse: ({mouse_x}, {mouse_y})")
        self.debug_display.add_message(f"Scroll: offset={self.scroll_offset}, max={self.max_scroll}")
        
        # Draw thumbnails
        for i, board in enumerate(config.AUTHORS):
            row = i // THUMBNAILS_PER_ROW
            col = i % THUMBNAILS_PER_ROW
            x = PADDING + col * (thumb_width + PADDING)
            y = PADDING + row * (thumb_height + PADDING + 60) - self.scroll_offset
            
            # Get or create thumbnail
            if board['file'] not in self.thumbnail_cache:
                thumbnail = pygame.image.load(board['file']).convert()
                thumbnail = pygame.transform.scale(thumbnail, (thumb_width, thumb_height))
                self.thumbnail_cache[board['file']] = thumbnail
            else:
                thumbnail = self.thumbnail_cache[board['file']]
            
            # Apply hover effect if this is the hovered thumbnail
            if i == self.hover_index and self.hover_effect:
                scaled_size, offset = self.hover_effect.get_state()
                # Calculate the center point of the original thumbnail
                center_x = x + thumb_width // 2
                center_y = y + thumb_height // 2
                # Scale the thumbnail
                hover_thumbnail = pygame.transform.scale(thumbnail, scaled_size)
                # Calculate new position to keep the thumbnail centered
                new_x = center_x - scaled_size[0] // 2
                new_y = center_y - scaled_size[1] // 2
                self.surface.blit(hover_thumbnail, (new_x, new_y))
                self.debug_display.add_message(f"Effect: {board['name']} - Scale: {scaled_size}")
            else:
                self.surface.blit(thumbnail, (x, y))
            
            # Draw board name centered over the thumbnail
            name_text = config.FONTS['selection'].render(board['name'], True, TITLE_COLOR)
            name_rect = name_text.get_rect(center=(x + thumb_width // 2, y + thumb_height // 2))
            self.surface.blit(name_text, name_rect)
            
            # Draw artist name with copyright symbol, centered below the thumbnail
            artist_text = config.FONTS['subtle'].render(f"© {board['artist']}", True, ARTIST_COLOR)
            text_rect = artist_text.get_rect(center=(x + thumb_width // 2, y + thumb_height + ARTIST_Y_OFFSET))
            self.surface.blit(artist_text, text_rect)
            
        # Reset clipping
        self.surface.set_clip(None)
        
        # Draw scroll indicator if content is scrollable
        if self.max_scroll > 0:
            scroll_height = (self.height - 120) * (self.height / (self.max_scroll + self.height))
            scroll_y = 60 + ((self.height - 120 - scroll_height) * (self.scroll_offset / self.max_scroll))
            pygame.draw.rect(self.surface, SCROLLBAR_COLOR, 
                           (self.width - 10, scroll_y, 5, scroll_height))
            
        # Draw debug messages
        self.debug_display.draw()
        
    def draw(self) -> None:
        """Draw the panel."""
        if not self.is_visible:
            return
            
        # Draw background
        self.surface.fill((0, 0, 0, 0))  # Clear with transparent color
        
        # Draw content
        self.draw_content()
        
        # Draw panel to screen with animation offset
        offset = self.animation_state['current_offset'] if self.animation_state['current'] else 0
        self.screen.blit(self.surface, (self.x, self.y + offset))
        
        # Draw decorative edge
        self.draw_edge(offset)
        
        # Draw debug display last so it's on top
        if config.IN_DEBUG_MODE:
            self.debug_display.draw()
            
    def draw_edge(self, offset: float) -> None:
        """Draw the decorative edge around the panel."""
        # Draw shadow
        shadow_rect = pygame.Rect(
            self.x - EDGE_THICKNESS + EDGE_SHADOW_OFFSET,
            self.y + offset - EDGE_THICKNESS + EDGE_SHADOW_OFFSET,
            self.width + EDGE_THICKNESS * 2,
            self.height + EDGE_THICKNESS * 2
        )
        pygame.draw.rect(self.screen, EDGE_SHADOW_COLOR, shadow_rect, EDGE_THICKNESS)
        
        # Draw main edge
        edge_rect = pygame.Rect(
            self.x - EDGE_THICKNESS,
            self.y + offset - EDGE_THICKNESS,
            self.width + EDGE_THICKNESS * 2,
            self.height + EDGE_THICKNESS * 2
        )
        pygame.draw.rect(self.screen, EDGE_COLOR, edge_rect, EDGE_THICKNESS)
        
    def is_point_in_panel(self, x: int, y: int) -> bool:
        """Check if a point is within the panel's bounds."""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height) 