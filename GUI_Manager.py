'''
Purpose: Manages user interface input and visual feedback.
Responsibilities:
 •	Monitors cursor hover, click, drag, and tap interactions.
 •	Shows visual cues (highlighting legal moves, mana costs, ability activation).
 •	Updates the display when cards are played, tapped, moved, flipped.
 •	Calls Util_Effects.py to animate the cards, tokens, hands and tapping etc.
'''

import pygame
import Util_Effects
import Util_Config as config


class GUI_Manager:
    def __init__(self) -> None:
        self.debug_text = "Debug Mode: ON"
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        pygame.display.set_caption("Sorcery: The Contested Realm")
        
        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    config.IN_DEBUG_MODE = not config.IN_DEBUG_MODE
     
    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(config.FPS)
            
        pygame.quit()

    def draw(self) -> None:
        """Draw the current game state."""
        self.screen.fill((255, 255, 255))
            
        # Draw debug info
        if config.IN_DEBUG_MODE:
            debug_surface = config.FONTS['debug'].render(self.debug_text, True, (244, 0, 244))
            self.screen.blit(debug_surface, (10, 10))
            
        pygame.display.flip()
        
    def draw_selection_screen(self, surface: pygame.Surface) -> None:
        """
        Draw the background selection screen.
        
        Args:
            surface: The pygame surface to draw on
        """
        surface.fill((203, 203, 203))
        
        # Update hover animation
        self.hover_effect.update()
        
        # Draw title
        title = config.FONTS['title'].render("Select Game Board", True, (0, 0, 0))
        title_rect = title.get_rect(centerx=surface.get_width() // 2, top=20)
        surface.blit(title, title_rect)
        
        # Calculate layout
        screen_width, screen_height = surface.get_size()
        padding = 50
        cols = 2  # Number of columns for thumbnails
        
        # Calculate thumbnail positions and draw
        for i, rect in enumerate(self.thumbnail_rects):
            col = i % cols
            row = i // cols
            x = padding + col * (config.THUMBNAIL_SIZE[0] + padding)
            y = padding + row * (config.THUMBNAIL_SIZE[1] + padding + 40) + 60  # Extra space for title
            
            # Calculate hover animation
            if i == self.hover_index:
                # Get scaled size and offset from hover effect
                scaled_size = self.hover_effect.get_scaled_size()
                offset_x, offset_y = self.hover_effect.get_offset(scaled_size)
                
                # Create hovered thumbnail
                hovered = pygame.transform.scale(self.thumbnails[i], scaled_size)
                hover_rect = hovered.get_rect()
                
                # Position the hovered thumbnail
                hover_rect.topleft = (x - offset_x, y - offset_y)
                
                # Draw hovered thumbnail
                surface.blit(hovered, hover_rect)
            else:
                # Draw normal thumbnail
                rect.topleft = (x, y)
                surface.blit(self.thumbnails[i], rect)
        
            # Draw selection text
            text = config.FONTS['selection'].render("Click to select", True, (0, 0, 0))
            text_rect = text.get_rect(
                centerx=x + config.THUMBNAIL_SIZE[0] // 2,
                top=y + config.THUMBNAIL_SIZE[1] + 10
            )
            surface.blit(text, text_rect)

    def draw_player_areas(self, surface, x, y, scale) -> None:
        """Draw the player deck and atlas areas."""
        if not self.selected_background:
            return

        # Get card size and scale it
        card_width = int(self.selected_background['card_size'][0] * scale)
        card_height = int(self.selected_background['card_size'][1] * scale)

        # Draw Player 1 areas (red)
        # Atlas (rotated 90 degrees)
        atlas_x = x + int(self.selected_background['p1_atlis'][0] * scale)
        atlas_y = y + int(self.selected_background['p1_atlis'][1] * scale)
        pygame.draw.rect(surface, config.PLAYER_COLORS['p1'], 
                         (atlas_x, atlas_y, card_height, card_width), 2)  # Swapped width/height for rotation
        
        # Spells
        spells_x = x + int(self.selected_background['p1_spells'][0] * scale)
        spells_y = y + int(self.selected_background['p1_spells'][1] * scale)
        pygame.draw.rect(surface, config.PLAYER_COLORS['p1'], 
                         (spells_x, spells_y, card_width, card_height), 2)
        
        # Graveyard
        grave_x = x + int(self.selected_background['p1_grave'][0] * scale)
        grave_y = y + int(self.selected_background['p1_grave'][1] * scale)
        pygame.draw.rect(surface, config.PLAYER_COLORS['p1'], 
                         (grave_x, grave_y, card_width, card_height), 2)

        # Draw Player 2 areas (blue)
        # Atlas (rotated 90 degrees)
        atlas_x = x + int(self.selected_background['p2_atlas'][0] * scale)
        atlas_y = y + int(self.selected_background['p2_atlas'][1] * scale)
        pygame.draw.rect(surface, config.PLAYER_COLORS['p2'], 
                         (atlas_x, atlas_y, card_height, card_width), 2)  # Swapped width/height for rotation
        
        # Spells
        spells_x = x + int(self.selected_background['p2_spells'][0] * scale)
        spells_y = y + int(self.selected_background['p2_spells'][1] * scale)
        pygame.draw.rect(surface, config.PLAYER_COLORS['p2'], 
                         (spells_x, spells_y, card_width, card_height), 2)
        
        # Graveyard
        grave_x = x + int(self.selected_background['p2_grave'][0] * scale)
        grave_y = y + int(self.selected_background['p2_grave'][1] * scale)
        pygame.draw.rect(surface, config.PLAYER_COLORS['p2'], 
                         (grave_x, grave_y, card_width, card_height), 2)

    def draw_grid(self, surface, x, y) -> None:
        """Draw the grid lines on the surface at the specified position."""
        if not self.background:
            return
            
        # Calculate scale factor
        scale = self.bg_rect.width / self.original_size[0]
            
        # Draw grid lines with scaled offset and size
        for row in range(config.SQUARE_GRID[1] + 1):
            # Horizontal lines
            start_x = x + self.scaled_offset[0]
            end_x = x + self.scaled_offset[0] + (config.SQUARE_GRID[0] * self.scaled_tile_size)
            line_y = y + self.scaled_offset[1] + (row * self.scaled_tile_size)
            pygame.draw.line(surface, self.grid_color, (start_x, line_y), (end_x, line_y), 2)
            
            # Vertical lines
            if row < config.SQUARE_GRID[1]:
                for col in range(config.SQUARE_GRID[0] + 1):
                    line_x = x + self.scaled_offset[0] + (col * self.scaled_tile_size)
                    start_y = y + self.scaled_offset[1]
                    end_y = y + self.scaled_offset[1] + (config.SQUARE_GRID[1] * self.scaled_tile_size)
                    pygame.draw.line(surface, self.grid_color, (line_x, start_y), (line_x, end_y), 2)
        # Draw player areas
        self.draw_player_areas(surface, x, y, scale)
        
    def select_background(self, index) -> None:
        """Select a background and initialize its properties."""
        if 0 <= index < len(self.backgrounds):
            self.selected_background = self.backgrounds[index]
            self.background = pygame.image.load(self.selected_background['path'])
            self.bg_rect = self.background.get_rect()
            self.original_size = self.bg_rect.size
            
            # Set grid properties from selected background
            self.original_grid_offset = (
                self.selected_background['grid_offset'][0],
                self.selected_background['grid_offset'][1]
            )
            self.original_tile_size = self.selected_background['grid_size'][0]

    def update_background_size(self, window_size) -> None:
        """Update background size based on window size while maintaining aspect ratio."""
        if not self.background:
            return
            
        window_width, window_height = window_size
        
        # Calculate scaling to maintain aspect ratio
        scale = min(window_width / self.original_size[0],
                    window_height / self.original_size[1])
        
        new_width = int(self.original_size[0] * scale)
        new_height = int(self.original_size[1] * scale)
        
        # Scale the background
        self.background = pygame.transform.scale(
            pygame.image.load(self.selected_background['path']), 
            (new_width, new_height)
        )
        self.bg_rect = self.background.get_rect()
        
        # Calculate scaled grid properties
        self.scaled_offset = (
            int(self.original_grid_offset[0] * scale),
            int(self.original_grid_offset[1] * scale)
        )
        self.scaled_tile_size = self.original_tile_size * scale
        