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
import sys
import time
import colorsys  # Add this import at the top
import Curiosa_Decks  # Add this import


class GUI_Manager:
    def __init__(self) -> None:
        self.debug_text = "Debug Mode: ON"
        pygame.init()
        
        # Set up the display for 1920x1080
        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        pygame.display.set_caption("Sorcery: The Contested Realm")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.hover_index = -1
        self.hover_effect = None  # Will be initialized when needed
        self.selected_board = None
        self.scroll_x = 0
        
        # Cache for board images
        self.board_image_cache = None
        self.board_rect_cache = None
        
        # Starting screen properties
        self.showing_start_screen = True
        self.fade_effect = Util_Effects.fade(start_alpha=0, end_alpha=255, duration=2.0, loop=False)
        self.title_image = pygame.image.load('assets/Icons/Sorcery Title.png').convert_alpha()
        self.title_rect = self.title_image.get_rect(center=(1920 // 2, int(1080 // 2)))
        
        # Selection screen properties
        self.background_image = pygame.image.load('assets/Icons/Sorcery_Screen.png').convert()
        self.background_rect = self.background_image.get_rect()
        self.zoom_scale = 1.0
        self.zoom_speed = 0.02
        self.zoom_direction = 1
        
        # Selection window slide effect
        self.selection_window_slide = None
        
        # Cache for thumbnails
        self.thumbnail_cache = {}
        
        # FPS tracking
        self.fps = 0
        self.fps_update_time = time.time()
        self.fps_update_interval = 0.5  # Update FPS display every 0.5 seconds
        
        # Create italic font for artist credits
        self.artist_font = pygame.font.SysFont('arial', 16, italic=True)
        
        # Load and cache Add Deck image
        self.add_deck_image = pygame.image.load('assets/Icons/Add Deck.png').convert_alpha()
        
        # Add Deck button properties
        self.add_deck_plus_effects = {
            'Player 1': Util_Effects.pulse((40, 40), scale_factor=0.05, speed=0.1),
            'Player 2': Util_Effects.pulse((40, 40), scale_factor=0.05, speed=0.1)
        }
        self.add_deck_hover = {'Player 1': False, 'Player 2': False}
        self.showing_deck_selection = False
        self.deck_selection_window_slide = None
        self.deck_hover_index = -1
        self.deck_hover_effect = None
        self.selected_deck = None
        self.deck_thumbnail_cache = {}
        
        # Deck categories
        self.deck_categories = {
            'Preconstructed Alpha': Curiosa_Decks.get_all_precon_alpha(),
            'Preconstructed Beta': Curiosa_Decks.get_all_precon_beta(),
            'Single Element': Curiosa_Decks.get_all_single_element(),
            'Double Element': Curiosa_Decks.get_all_double_element(),
            'Triple Element': Curiosa_Decks.get_all_triple_element(),
            'Quadruple Element': Curiosa_Decks.get_all_quadruple_element()
        }
        
        # Current category being displayed
        self.current_category = 'Preconstructed Alpha'
        self.category_hover_index = -1
        self.category_hover_effect = None

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    config.IN_DEBUG_MODE = not config.IN_DEBUG_MODE
                elif event.key == pygame.K_p:  # Add 'P' key to toggle profiling
                    config.IN_PROFILING_MODE = not config.IN_PROFILING_MODE
                    print(f"Profiling mode: {'Enabled' if config.IN_PROFILING_MODE else 'Disabled'}")
                elif event.key == pygame.K_RETURN and self.showing_start_screen:
                    self.showing_start_screen = False
                    self.fade_effect.reset()  # Reset fade effect for next use
                    # Initialize slide effect for selection window
                    window_height = self.screen.get_height()
                    self.selection_window_slide = Util_Effects.slide(
                        start_pos=(0, window_height),  # Start below screen
                        end_pos=(0, int(window_height * 0.05)),  # End at 5% from top
                        duration=0.8  # Slightly longer animation
                    )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.showing_start_screen:
                    self.showing_start_screen = False
                    self.fade_effect.reset()  # Reset fade effect for next use
                    # Initialize slide effect for selection window
                    window_height = self.screen.get_height()
                    self.selection_window_slide = Util_Effects.slide(
                        start_pos=(0, window_height),  # Start below screen
                        end_pos=(0, int(window_height * 0.05)),  # End at 5% from top
                        duration=0.8  # Slightly longer animation
                    )
                elif not self.selected_board:  # Only handle board selection if no board is selected
                    mouse_x, mouse_y = event.pos
                    window_width = self.screen.get_width()
                    window_height = self.screen.get_height()
                    
                    # Calculate selection window dimensions (90% of window size)
                    selection_width = int(window_width * 0.9)
                    selection_height = int(window_height * 0.9)
                    selection_x = (window_width - selection_width) // 2
                    selection_y = (window_height - selection_height) // 2
                    
                    # Check if click is within selection window
                    if (selection_x <= mouse_x <= selection_x + selection_width and
                        selection_y <= mouse_y <= selection_y + selection_height):
                        
                        # Calculate thumbnail dimensions
                        padding = 30
                        thumbnails_per_row = 5
                        thumb_width = (selection_width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
                        thumb_height = int(thumb_width * 0.7)
                        
                        # Check which thumbnail was clicked
                        for i, board in enumerate(config.AUTHORS):
                            row = i // thumbnails_per_row
                            col = i % thumbnails_per_row
                            x = selection_x + padding + col * (thumb_width + padding)
                            y = selection_y + (selection_height * 0.3 if row == 0 else selection_height * 0.6)
                            rect = pygame.Rect(x, y, thumb_width, thumb_height)
                            if rect.collidepoint(mouse_x, mouse_y):
                                self.selected_board = board
                                break
                elif event.button == 4:  # Scroll up
                    self.scroll_x = max(0, self.scroll_x - 50)
                elif event.button == 5:  # Scroll down
                    self.scroll_x += 50
                elif self.selected_board and not self.showing_deck_selection:
                    # Check for Add Deck button clicks
                    mouse_x, mouse_y = event.pos
                    window_width = self.screen.get_width()
                    window_height = self.screen.get_height()
                    
                    # Calculate grid position
                    grid_width = 5
                    grid_height = 4
                    tile_width = (window_width - 80) / 6.6
                    card_height = tile_width / 2
                    card_width = card_height / 1.4
                    scale = min(
                        (window_width - 60) / (5 * tile_width + 80 + 2 * card_width),
                        (window_height - 60) / (4 * tile_width + 60)
                    )
                    tile_size = int(tile_width * scale)
                    total_grid_width = grid_width * tile_size
                    total_grid_height = grid_height * tile_size
                    grid_x = (window_width - total_grid_width) // 2
                    grid_y = (window_height - total_grid_height) // 2
                    middle_y = grid_y + (2 * tile_size)
                    
                    # Check Player 1 Add Deck button (right side)
                    p1_add_deck_rect = pygame.Rect(
                        window_width // 2 + 150 - 50,  # Center + offset - half width
                        middle_y - 40,  # Just above middle line
                        100,  # Button width
                        40   # Button height
                    )
                    if p1_add_deck_rect.collidepoint(mouse_x, mouse_y):
                        self.showing_deck_selection = True
                        self.deck_selection_window_slide = Util_Effects.slide(
                            start_pos=(0, window_height),
                            end_pos=(0, int(window_height * 0.05)),
                            duration=0.8
                        )
                    
                    # Check Player 2 Add Deck button (left side)
                    p2_add_deck_rect = pygame.Rect(
                        window_width // 2 - 150 - 50,  # Center - offset - half width
                        middle_y - 40,  # Just above middle line
                        100,  # Button width
                        40   # Button height
                    )
                    if p2_add_deck_rect.collidepoint(mouse_x, mouse_y):
                        self.showing_deck_selection = True
                        self.deck_selection_window_slide = Util_Effects.slide(
                            start_pos=(0, window_height),
                            end_pos=(0, int(window_height * 0.05)),
                            duration=0.8
                        )
                elif self.showing_deck_selection:
                    # Handle category button clicks
                    mouse_x, mouse_y = event.pos
                    window_width = self.screen.get_width()
                    window_height = self.screen.get_height()
                    
                    # Calculate selection window dimensions
                    selection_width = int(window_width * 0.9)
                    selection_height = int(window_height * 0.9)
                    selection_x = (window_width - selection_width) // 2
                    selection_y = int(window_height * 0.05)
                    
                    # Check category buttons
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
                            break
                    
                    # Handle deck selection clicks
                    padding = 30
                    thumbnails_per_row = 3
                    thumb_width = (selection_width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
                    thumb_height = int(thumb_width * 1.4)
                    
                    decks = self.deck_categories[self.current_category]
                    for i, deck_url in enumerate(decks):
                        row = i // thumbnails_per_row
                        col = i % thumbnails_per_row
                        x = selection_x + padding + col * (thumb_width + padding)
                        y = category_y + category_height + 40 + row * (thumb_height + padding + 40)
                        rect = pygame.Rect(x, y, thumb_width, thumb_height)
                        if rect.collidepoint(mouse_x, mouse_y):
                            self.selected_deck = deck_url
                            # Get full deck data when selected
                            try:
                                deck_data = Curiosa_Decks.get_deck_json_from_curiosa(deck_url)
                                # TODO: Pass deck_data to Game_Manager to create the actual deck
                                self.showing_deck_selection = False
                            except Exception as e:
                                print(f"Error loading deck: {e}")
                                # TODO: Show error message to user
                            break
            elif event.type == pygame.MOUSEMOTION and not self.showing_start_screen:
                if self.selected_board and not self.showing_deck_selection:
                    # Update hover state for Add Deck buttons
                    mouse_x, mouse_y = event.pos
                    window_width = self.screen.get_width()
                    window_height = self.screen.get_height()
                    
                    # Calculate grid position
                    grid_width = 5
                    grid_height = 4
                    tile_width = (window_width - 80) / 6.6
                    card_height = tile_width / 2
                    card_width = card_height / 1.4
                    scale = min(
                        (window_width - 60) / (5 * tile_width + 80 + 2 * card_width),
                        (window_height - 60) / (4 * tile_width + 60)
                    )
                    tile_size = int(tile_width * scale)
                    total_grid_width = grid_width * tile_size
                    total_grid_height = grid_height * tile_size
                    grid_x = (window_width - total_grid_width) // 2
                    grid_y = (window_height - total_grid_height) // 2
                    middle_y = grid_y + (2 * tile_size)
                    
                    # Check Player 1 Add Deck button
                    p1_add_deck_rect = pygame.Rect(
                        grid_x + (5 * tile_size) + 30 + card_width // 2 - 50,
                        middle_y - 100,
                        100,
                        40
                    )
                    self.add_deck_hover['Player 1'] = p1_add_deck_rect.collidepoint(mouse_x, mouse_y)
                    
                    # Check Player 2 Add Deck button
                    p2_add_deck_rect = pygame.Rect(
                        grid_x - 30 - card_width // 2 - 50,
                        middle_y + 60,
                        100,
                        40
                    )
                    self.add_deck_hover['Player 2'] = p2_add_deck_rect.collidepoint(mouse_x, mouse_y)
                elif self.showing_deck_selection:
                    # Update hover state for category buttons
                    mouse_x, mouse_y = event.pos
                    window_width = self.screen.get_width()
                    window_height = self.screen.get_height()
                    
                    # Calculate selection window dimensions
                    selection_width = int(window_width * 0.9)
                    selection_height = int(window_height * 0.9)
                    selection_x = (window_width - selection_width) // 2
                    selection_y = int(window_height * 0.05)
                    
                    # Check category buttons
                    category_padding = 20
                    category_width = 200
                    category_height = 40
                    category_y = selection_y + 80
                    
                    for i, category in enumerate(self.deck_categories.keys()):
                        category_x = selection_x + category_padding + i * (category_width + category_padding)
                        category_rect = pygame.Rect(category_x, category_y, category_width, category_height)
                        if category_rect.collidepoint(mouse_x, mouse_y):
                            if self.category_hover_index != i:
                                self.category_hover_index = i
                                self.category_hover_effect = Util_Effects.pulse((category_width, category_height), scale_factor=0.05)
                            break
                    else:
                        if self.category_hover_index != -1:
                            self.category_hover_index = -1
                            self.category_hover_effect = None
                    
                    # Update hover state for deck thumbnails
                    padding = 30
                    thumbnails_per_row = 3
                    thumb_width = (selection_width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
                    thumb_height = int(thumb_width * 1.4)
                    
                    decks = self.deck_categories[self.current_category]
                    for i, deck_url in enumerate(decks):
                        row = i // thumbnails_per_row
                        col = i % thumbnails_per_row
                        x = selection_x + padding + col * (thumb_width + padding)
                        y = category_y + category_height + 40 + row * (thumb_height + padding + 40)
                        rect = pygame.Rect(x, y, thumb_width, thumb_height)
                        if rect.collidepoint(mouse_x, mouse_y):
                            if self.deck_hover_index != i:
                                self.deck_hover_index = i
                                self.deck_hover_effect = Util_Effects.pulse((thumb_width, thumb_height), scale_factor=0.05)
                            break
                    else:
                        if self.deck_hover_index != -1:
                            self.deck_hover_index = -1
                            self.deck_hover_effect = None
                
                # Update hover index based on mouse position
                mouse_x, mouse_y = event.pos
                window_width = self.screen.get_width()
                window_height = self.screen.get_height()
                
                # Calculate selection window dimensions (90% of window size)
                selection_width = int(window_width * 0.9)
                selection_height = int(window_height * 0.9)
                selection_x = (window_width - selection_width) // 2
                selection_y = (window_height - selection_height) // 2
                
                # Check if mouse is within selection window
                if (selection_x <= mouse_x <= selection_x + selection_width and
                    selection_y <= mouse_y <= selection_y + selection_height):
                    
                    # Calculate thumbnail dimensions
                    padding = 30
                    thumbnails_per_row = 5
                    thumb_width = (selection_width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
                    thumb_height = int(thumb_width * 0.7)
                    
                    # Calculate which thumbnail is being hovered
                    for i, board in enumerate(config.AUTHORS):
                        row = i // thumbnails_per_row
                        col = i % thumbnails_per_row
                        x = selection_x + padding + col * (thumb_width + padding)
                        y = selection_y + (selection_height * 0.3 if row == 0 else selection_height * 0.6)
                        rect = pygame.Rect(x, y, thumb_width, thumb_height)
                        if rect.collidepoint(mouse_x, mouse_y):
                            if self.hover_index != i:
                                self.hover_index = i
                                # Initialize hover effect with current thumbnail size
                                self.hover_effect = Util_Effects.pulse((thumb_width, thumb_height), scale_factor=0.05)
                            break
                    else:
                        if self.hover_index != -1:
                            self.hover_index = -1
                            self.hover_effect = None
                else:
                    if self.hover_index != -1:
                        self.hover_index = -1
                        self.hover_effect = None

    def run(self) -> None:
        """Main game loop."""
        import cProfile
        import pstats
        import os
        import tempfile
        
        # Initialize profiling if enabled
        pr = None
        profile_file = None
        if config.IN_PROFILING_MODE:
            profile_file = os.path.join(tempfile.gettempdir(), 'sorcery_profile.prof')
            pr = cProfile.Profile()
            # Set a lower sampling rate to reduce overhead
            pr.enable(subcalls=False, builtins=False)
        
        try:
            while self.running:
                # Only profile specific sections if profiling is enabled
                if config.IN_PROFILING_MODE and pr is not None:
                    pr.enable(subcalls=False, builtins=False)
                
                self.handle_events()
                
                # Update all effects every frame
                if self.hover_effect:
                    self.hover_effect.update()
                if self.showing_start_screen:
                    self.fade_effect.update()
                if self.selection_window_slide:
                    self.selection_window_slide.update()
                if self.deck_selection_window_slide:
                    self.deck_selection_window_slide.update()
                
                # Update Add Deck plus effects
                for effect in self.add_deck_plus_effects.values():
                    effect.update()
                
                # Update deck hover effect
                if self.deck_hover_effect:
                    self.deck_hover_effect.update()
                
                # Update category hover effect
                if self.category_hover_effect:
                    self.category_hover_effect.update()
                
                if config.IN_PROFILING_MODE and pr is not None:
                    pr.disable()
                
                # Drawing operations
                if self.showing_start_screen:
                    self.draw_start_screen()
                elif not self.selected_board:
                    self.draw_selection_screen()
                elif self.showing_deck_selection:
                    self.draw_deck_selection_screen()
                else:
                    self.draw()
                    
                # Update and display FPS
                current_time = time.time()
                if current_time - self.fps_update_time >= self.fps_update_interval:
                    self.fps = int(self.clock.get_fps())  # Convert to integer
                    self.fps_update_time = current_time
                
                if config.IN_DEBUG_MODE:
                    fps_text = config.FONTS['debug'].render(f"FPS: {self.fps}", True, (255, 255, 255))
                    self.screen.blit(fps_text, (10, 10))
                    
                pygame.display.flip()
                self.clock.tick(config.FPS)
        finally:
            # Stop profiling if it was enabled
            if config.IN_PROFILING_MODE and pr is not None:
                pr.disable()
                pr.dump_stats(profile_file)
                
                # Print instructions for viewing the profile
                print("\nProfiling data saved to:", profile_file)
                print("To view the profile visualization, run:")
                print("pip install snakeviz")
                print("snakeviz", profile_file)
            
            pygame.quit()
            sys.exit()

    def draw_start_screen(self) -> None:
        """Draw the starting screen with fade-in title."""
        # Fill with dark metal grey
        self.screen.fill((40, 40, 40))
        
        # Get current fade alpha from effect
        alpha = self.fade_effect.get_state()
        
        # Create a copy of the title image with current alpha
        title_surface = self.title_image.copy()
        title_surface.set_alpha(alpha)
        
        # Draw the title
        self.screen.blit(title_surface, self.title_rect)
        
        # Draw "Press Enter or Click to Start" text only if we're still on start screen
        # and the fade is complete
        if self.showing_start_screen and alpha >= 255:
            start_text = config.FONTS['subtitle'].render("Press Enter or Click to Start", True, (200, 200, 200))
            text_rect = start_text.get_rect(center=(1920 // 2, int(1080 * 0.9)))
            self.screen.blit(start_text, text_rect)

    def draw_selection_screen(self) -> None:
        """Draw the background selection screen."""
        # Get window dimensions
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Clear the screen first
        self.screen.fill((40, 40, 40))  # Fill with dark background
        
        # Calculate 90% of window dimensions for selection window
        selection_width = int(window_width * 0.9)
        selection_height = int(window_height * 0.9)
        selection_x = (window_width - selection_width) // 2
        
        # Calculate background scaling
        target_width = selection_width
        target_height = selection_height
        
        # Calculate scale to maintain aspect ratio
        width_scale = target_width / self.background_rect.width
        height_scale = target_height / self.background_rect.height
        base_scale = min(width_scale, height_scale)
        
        # Update zoom effect
        self.zoom_scale = base_scale + (self.zoom_speed * self.zoom_direction)
        if self.zoom_scale >= base_scale * 1.1 or self.zoom_scale <= base_scale * 0.9:
            self.zoom_direction *= -1
        
        # Calculate zoomed size
        zoomed_width = int(self.background_rect.width * self.zoom_scale)
        zoomed_height = int(self.background_rect.height * self.zoom_scale)
        
        # Scale background with zoom effect
        zoomed_bg = pygame.transform.scale(self.background_image, (zoomed_width, zoomed_height))
        
        # Center the zoomed background
        bg_x = (window_width - zoomed_width) // 2
        bg_y = (window_height - zoomed_height) // 2
        
        # Draw the zooming background
        self.screen.blit(zoomed_bg, (bg_x, bg_y))
        
        # Create a surface for the selection window with a semi-transparent background
        selection_surface = pygame.Surface((selection_width, selection_height), pygame.SRCALPHA)
        # Fill with semi-transparent black
        selection_surface.fill((0, 0, 0, 200))  # Black with 200 alpha
        
        # Draw 3D border effect
        border_width = 4  # Width of the border
        
        # Base gold color in RGB
        base_gold = (170, 149, 96)  # Goldenrod
        
        # Convert RGB to HSV using colorsys
        h, s, v = colorsys.rgb_to_hsv(base_gold[0] / 255.0, base_gold[1] / 255.0, base_gold[2] / 255.0)
        
        # Create highlight (increase saturation and value)
        highlight_h, highlight_s, highlight_v = h, min(1.0, s * 1.2), min(1.0, v * 1.2)
        highlight_rgb = colorsys.hsv_to_rgb(highlight_h, highlight_s, highlight_v)
        highlight_gold = (int(highlight_rgb[0] * 255), int(highlight_rgb[1] * 255), 
                         int(highlight_rgb[2] * 255), 255)
        
        # Create shadow (decrease saturation and value)
        shadow_h, shadow_s, shadow_v = h, max(0.0, s * 0.8), max(0.0, v * 0.8)
        shadow_rgb = colorsys.hsv_to_rgb(shadow_h, shadow_s, shadow_v)
        shadow_gold = (int(shadow_rgb[0] * 255), int(shadow_rgb[1] * 255), 
                      int(shadow_rgb[2] * 255), 255)
        
        # Draw the border with proper 3D effect
        # Top edge: highlight on outside, shadow on inside
        pygame.draw.line(selection_surface, highlight_gold, (0, 0), (selection_width, 0), border_width // 2)
        pygame.draw.line(selection_surface, shadow_gold, (0, border_width // 2), 
                        (selection_width, border_width // 2), border_width // 2)
        
        # Left edge: highlight on outside, shadow on inside
        pygame.draw.line(selection_surface, highlight_gold, (0, 0), (0, selection_height), border_width // 2)
        pygame.draw.line(selection_surface, shadow_gold, (border_width // 2, 0), 
                        (border_width // 2, selection_height), border_width // 2)
        
        # Bottom edge: highlight on inside, shadow on outside
        pygame.draw.line(selection_surface, shadow_gold, (0, selection_height - border_width), 
                        (selection_width, selection_height - border_width), border_width // 2)
        pygame.draw.line(selection_surface, highlight_gold, (0, selection_height - border_width // 2), 
                        (selection_width, selection_height - border_width // 2), border_width // 2)
        
        # Right edge: highlight on inside, shadow on outside
        pygame.draw.line(selection_surface, shadow_gold, (selection_width - border_width, 0), 
                        (selection_width - border_width, selection_height), border_width // 2)
        pygame.draw.line(selection_surface, highlight_gold, (selection_width - border_width // 2, 0), 
                        (selection_width - border_width // 2, selection_height), border_width // 2)
        
        # Draw title within selection window, 30 pixels from top
        title = config.FONTS['title'].render("Select Game Board", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=selection_width // 2, centery=30)
        selection_surface.blit(title, title_rect)
        
        # Calculate layout for two rows of thumbnails
        padding = 30
        thumbnails_per_row = 5
        
        # Calculate thumbnail size
        thumb_width = (selection_width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
        thumb_height = int(thumb_width * 0.7)
        
        # Draw thumbnails
        for i, board in enumerate(config.AUTHORS):
            row = i // thumbnails_per_row
            col = i % thumbnails_per_row
            x = padding + col * (thumb_width + padding)
            y = (selection_height * 0.3 if row == 0 else selection_height * 0.6)
            
            # Get or create thumbnail
            board_file = board['file']  # Use the file path as the cache key
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
                selection_surface.blit(scaled_thumbnail, (x - offset[0], y - offset[1]))
            else:
                selection_surface.blit(thumbnail, (x, y))
            
            # Draw artist credit
            credit_text = self.artist_font.render(board['artist'], True, (200, 200, 200))
            credit_rect = credit_text.get_rect(centerx=x + thumb_width // 2, top=y + thumb_height + 5)
            selection_surface.blit(credit_text, credit_rect)
        
        # Apply slide effect to the selection window
        if self.selection_window_slide:
            current_pos, _ = self.selection_window_slide.get_state()
            # Draw the selection surface at the current slide position
            self.screen.blit(selection_surface, (selection_x, current_pos[1]))
        else:
            # Draw at the default position (5% from top)
            self.screen.blit(selection_surface, (selection_x, int(window_height * 0.05)))

    def draw_deck_selection_screen(self) -> None:
        """Draw the deck selection screen."""
        # Get window dimensions
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Clear the screen first
        self.screen.fill((40, 40, 40))  # Fill with dark background
        
        # Calculate 90% of window dimensions for selection window
        selection_width = int(window_width * 0.9)
        selection_height = int(window_height * 0.9)
        selection_x = (window_width - selection_width) // 2
        
        # Create a surface for the selection window with a semi-transparent background
        selection_surface = pygame.Surface((selection_width, selection_height), pygame.SRCALPHA)
        # Fill with semi-transparent black
        selection_surface.fill((0, 0, 0, 200))  # Black with 200 alpha
        
        # Draw 3D border effect (same as board selection)
        border_width = 4
        base_gold = (170, 149, 96)
        h, s, v = colorsys.rgb_to_hsv(base_gold[0] / 255.0, base_gold[1] / 255.0, base_gold[2] / 255.0)
        
        highlight_h, highlight_s, highlight_v = h, min(1.0, s * 1.2), min(1.0, v * 1.2)
        highlight_rgb = colorsys.hsv_to_rgb(highlight_h, highlight_s, highlight_v)
        highlight_gold = (int(highlight_rgb[0] * 255), int(highlight_rgb[1] * 255), 
                         int(highlight_rgb[2] * 255), 255)
        
        shadow_h, shadow_s, shadow_v = h, max(0.0, s * 0.8), max(0.0, v * 0.8)
        shadow_rgb = colorsys.hsv_to_rgb(shadow_h, shadow_s, shadow_v)
        shadow_gold = (int(shadow_rgb[0] * 255), int(shadow_rgb[1] * 255), 
                      int(shadow_rgb[2] * 255), 255)
        
        # Draw border lines
        pygame.draw.line(selection_surface, highlight_gold, (0, 0), (selection_width, 0), border_width // 2)
        pygame.draw.line(selection_surface, shadow_gold, (0, border_width // 2), 
                        (selection_width, border_width // 2), border_width // 2)
        
        pygame.draw.line(selection_surface, highlight_gold, (0, 0), (0, selection_height), border_width // 2)
        pygame.draw.line(selection_surface, shadow_gold, (border_width // 2, 0), 
                        (border_width // 2, selection_height), border_width // 2)
        
        pygame.draw.line(selection_surface, shadow_gold, (0, selection_height - border_width), 
                        (selection_width, selection_height - border_width), border_width // 2)
        pygame.draw.line(selection_surface, highlight_gold, (0, selection_height - border_width // 2), 
                        (selection_width, selection_height - border_width // 2), border_width // 2)
        
        pygame.draw.line(selection_surface, shadow_gold, (selection_width - border_width, 0), 
                        (selection_width - border_width, selection_height), border_width // 2)
        pygame.draw.line(selection_surface, highlight_gold, (selection_width - border_width // 2, 0), 
                        (selection_width - border_width // 2, selection_height), border_width // 2)
        
        # Draw title
        title = config.FONTS['title'].render("Select Deck", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=selection_width // 2, centery=30)
        selection_surface.blit(title, title_rect)
        
        # Draw category buttons
        category_padding = 20
        category_width = 200
        category_height = 40
        category_y = 80
        
        for i, category in enumerate(self.deck_categories.keys()):
            category_x = selection_x + category_padding + i * (category_width + category_padding)
            
            # Draw category button background
            if i == self.category_hover_index:
                pygame.draw.rect(selection_surface, (100, 100, 100, 200),
                               (category_x, category_y, category_width, category_height))
            
            # Draw category button border
            pygame.draw.rect(selection_surface, highlight_gold if i == self.category_hover_index else shadow_gold,
                           (category_x, category_y, category_width, category_height), 2)
            
            # Draw category name
            category_text = config.FONTS['subtitle'].render(category, True, (255, 255, 255))
            category_rect = category_text.get_rect(center=(category_x + category_width // 2,
                                                         category_y + category_height // 2))
            selection_surface.blit(category_text, category_rect)
        
        # Calculate layout for deck thumbnails
        padding = 30
        thumbnails_per_row = 3
        
        # Calculate thumbnail size
        thumb_width = (selection_width - (padding * (thumbnails_per_row + 1))) // thumbnails_per_row
        thumb_height = int(thumb_width * 1.4)  # Card aspect ratio
        
        # Draw deck thumbnails for current category
        decks = self.deck_categories[self.current_category]
        for i, deck_url in enumerate(decks):
            row = i // thumbnails_per_row
            col = i % thumbnails_per_row
            x = padding + col * (thumb_width + padding)
            y = category_y + category_height + 40 + row * (thumb_height + padding + 40)  # Extra space for description
            
            # Get or create thumbnail
            if deck_url not in self.deck_thumbnail_cache:
                try:
                    # Extract deck ID from URL
                    deck_id = deck_url.split('/')[-1]
                    # Create a placeholder thumbnail with deck ID
                    thumbnail = pygame.Surface((thumb_width, thumb_height), pygame.SRCALPHA)
                    thumbnail.fill((100, 100, 100, 128))
                    
                    # Draw deck ID on thumbnail
                    id_text = config.FONTS['subtle'].render(deck_id[:8], True, (255, 255, 255))
                    id_rect = id_text.get_rect(center=(thumb_width // 2, thumb_height // 2))
                    thumbnail.blit(id_text, id_rect)
                    
                    self.deck_thumbnail_cache[deck_url] = thumbnail
                except Exception as e:
                    print(f"Error loading deck thumbnail: {e}")
                    # Create a placeholder
                    thumbnail = pygame.Surface((thumb_width, thumb_height), pygame.SRCALPHA)
                    thumbnail.fill((100, 100, 100, 128))
                    self.deck_thumbnail_cache[deck_url] = thumbnail
            else:
                thumbnail = self.deck_thumbnail_cache[deck_url]
            
            # Apply hover effect if this is the hovered thumbnail
            if i == self.deck_hover_index and self.deck_hover_effect:
                scaled_size, offset = self.deck_hover_effect.get_state()
                scaled_thumbnail = pygame.transform.scale(thumbnail, scaled_size)
                selection_surface.blit(scaled_thumbnail, (x - offset[0], y - offset[1]))
            else:
                selection_surface.blit(thumbnail, (x, y))
            
            # Draw deck URL
            deck_text = config.FONTS['subtle'].render(deck_url.split('/')[-1], True, (255, 255, 255))
            deck_rect = deck_text.get_rect(centerx=x + thumb_width // 2, top=y + thumb_height + 5)
            selection_surface.blit(deck_text, deck_rect)
        
        # Apply slide effect to the selection window
        if self.deck_selection_window_slide:
            current_pos, _ = self.deck_selection_window_slide.get_state()
            self.screen.blit(selection_surface, (selection_x, current_pos[1]))
        else:
            self.screen.blit(selection_surface, (selection_x, int(window_height * 0.05)))

    def draw(self) -> None:
        """Draw the current game state."""
        if not self.selected_board:
            return
            
        # Fill with dark background
        self.screen.fill((40, 40, 40))
        
        # Use cached board image or load it if not cached
        if self.board_image_cache is None:
            self.board_image_cache = pygame.image.load(self.selected_board['file']).convert()
            self.board_rect_cache = self.board_image_cache.get_rect()
        
        # Calculate window size based on board aspect ratio
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate target window size maintaining board aspect ratio
        target_width = window_width
        target_height = int(target_width * (self.board_rect_cache.height / self.board_rect_cache.width))
        
        if target_height > window_height:
            target_height = window_height
            target_width = int(target_height * (self.board_rect_cache.width / self.board_rect_cache.height))
        
        # Resize window if needed
        if target_width != window_width or target_height != window_height:
            self.screen = pygame.display.set_mode((target_width, target_height), pygame.RESIZABLE)
            window_width = target_width
            window_height = target_height
        
        # Scale the board image to fit the window
        scaled_board = pygame.transform.scale(self.board_image_cache, (window_width, window_height))
        
        # Draw the board image
        self.screen.blit(scaled_board, (0, 0))
        
        # Draw grid and player areas
        self.draw_grid(self.screen, 0, 0)
        
        # Draw debug info
        if config.IN_DEBUG_MODE:
            debug_surface = config.FONTS['debug'].render(self.debug_text, True, (244, 0, 244))
            self.screen.blit(debug_surface, (10, 10))
            
        pygame.display.flip()

    def draw_grid(self, surface, x, y) -> None:
        """Draw the grid lines on the surface at the specified position."""
        if not self.selected_board:
            return
            
        # Calculate grid properties based on the selected board
        grid_width = 5  # Number of columns
        grid_height = 4  # Number of rows
        
        # Get window dimensions
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Use cached board rect
        board_rect = self.board_rect_cache
        
        # Calculate tile size based on board image dimensions
        tile_width = (board_rect.width - 80) / 6.6
        
        # Calculate card dimensions - longer side is half tile size
        # For portrait cards (deck and graveyard)
        card_height = tile_width / 2  # Longer side is half tile size
        card_width = card_height / 1.4  # Width is height/1.4 for standard card ratio
        
        # Scale everything to fit the window while maintaining aspect ratio
        scale = min(
            (window_width - 60) / (5 * tile_width + 80 + 2 * card_width),  # Width scale
            (window_height - 60) / (4 * tile_width + 60)  # Height scale
        )
        
        # Apply scaling
        tile_size = int(tile_width * scale)
        card_width = int(card_width * scale)
        card_height = int(card_height * scale)
        
        # Calculate total grid dimensions
        total_grid_width = grid_width * tile_size
        total_grid_height = grid_height * tile_size
        
        # Calculate grid position to center it
        grid_x = (window_width - total_grid_width) // 2
        grid_y = (window_height - total_grid_height) // 2
        
        # Draw grid lines and tile numbers
        tile_number = 1
        for row in range(grid_height):
            for col in range(grid_width):
                # Calculate tile position
                tile_x = grid_x + (col * tile_size)
                tile_y = grid_y + (row * tile_size)
                
                # Draw tile number in top-left corner
                number_text = config.FONTS['subtle'].render(str(tile_number), True, (200, 200, 200))
                number_rect = number_text.get_rect(topleft=(tile_x + 5, tile_y + 5))  # 5px padding
                surface.blit(number_text, number_rect)
                
                tile_number += 1
        
        # Draw grid lines
        for row in range(grid_height + 1):
            # Horizontal lines
            start_x = grid_x
            end_x = grid_x + total_grid_width
            line_y = grid_y + (row * tile_size)
            pygame.draw.line(surface, (255, 255, 255), (start_x, line_y), (end_x, line_y), 2)
            
            # Vertical lines
            if row < grid_height:
                for col in range(grid_width + 1):
                    line_x = grid_x + (col * tile_size)
                    start_y = grid_y
                    end_y = grid_y + total_grid_height
                    pygame.draw.line(surface, (255, 255, 255), (line_x, start_y), (line_x, end_y), 2)
        
        # Draw player areas
        self.draw_player_areas(surface, grid_x, grid_y, tile_size, card_width, card_height)

    def draw_player_areas(self, surface, grid_x, grid_y, tile_size, card_width, card_height) -> None:
        """Draw the player deck and atlas areas."""
        if not self.selected_board:
            return
        
        # Calculate middle line position
        middle_y = grid_y + (2 * tile_size)  # Middle line is between rows 2 and 3
        window_width = self.screen.get_width()
        
        # Scale image to match 50% of tile size while maintaining aspect ratio
        image_ratio = self.add_deck_image.get_width() / self.add_deck_image.get_height()
        scaled_width = tile_size // 2  # 50% of tile size
        scaled_height = int(scaled_width / image_ratio)
        
        # Cache the base scaled image
        if not hasattr(self, '_cached_scaled_image') or self._cached_scaled_image.get_size() != (scaled_width, scaled_height):
            self._cached_scaled_image = pygame.transform.scale(self.add_deck_image, (scaled_width, scaled_height))
        
        add_deck_rect = self._cached_scaled_image.get_rect()
        
        # Player 1 areas (right side)
        # Draw Add Deck button for Player 1
        add_deck_rect.midtop = (window_width // 2 + 150, middle_y - 40)  # Increased spacing from center
        
        # Draw pulsing effect
        plus_size, plus_offset = self.add_deck_plus_effects['Player 1'].get_state()
        pulse_scaled = pygame.transform.scale(self._cached_scaled_image, 
            (int(scaled_width * (1 + plus_offset[0]/100)), 
             int(scaled_height * (1 + plus_offset[1]/100))))
        surface.blit(pulse_scaled, 
            (add_deck_rect.centerx - pulse_scaled.get_width()//2,
             add_deck_rect.top))
        
        # Draw Player 1 label
        player1_text = config.FONTS['text'].render("Player 1", True, config.COLOURS['Player 1'])
        player1_rect = player1_text.get_rect()
        player1_rect.midtop = (grid_x + (5 * tile_size) + 30 + card_width // 2, middle_y - 20)  # Just above middle
        surface.blit(player1_text, player1_rect)
        
        # Horizontal card (Atlas) near the middle, slightly below middle line
        atlas_x = grid_x + (5 * tile_size) + 30  # Right of grid + 30px spacing
        atlas_y = middle_y + 20  # 20px below middle line
        pygame.draw.rect(surface, config.COLOURS['Player 1'], 
                        (atlas_x, atlas_y, card_height, card_width), 2)  # Landscape orientation so card_width is y size
        
        # Draw "Atlas" label
        atlas_text = config.FONTS['subtle'].render("Atlas", True, config.COLOURS['Player 1'])
        atlas_rect = atlas_text.get_rect(center=(atlas_x + card_height // 2, atlas_y + card_width // 2))
        surface.blit(atlas_text, atlas_rect)
        
        # Vertical cards (Deck and Graveyard) below the horizontal card
        deck_x = atlas_x + (card_height - card_width) // 2  # Center under the horizontal card
        deck_y = atlas_y + card_width + 30  # 30px gap
        pygame.draw.rect(surface, config.COLOURS['Player 1'], 
                        (deck_x, deck_y, card_width, card_height), 2)  # Portrait orientation so card_width is x size
        
        # Draw "Spells" label
        spells_text = config.FONTS['subtle'].render("Spells", True, config.COLOURS['Player 1'])
        spells_rect = spells_text.get_rect(center=(deck_x + card_width // 2, deck_y + card_height // 2))
        surface.blit(spells_text, spells_rect)
        
        grave_x = deck_x
        grave_y = deck_y + card_height + 30  # 30px gap
        pygame.draw.rect(surface, config.COLOURS['Player 1'], 
                        (grave_x, grave_y, card_width, card_height), 2)  # Portrait orientation so card_width is x size
        
        # Draw "Grave" label
        grave_text = config.FONTS['subtle'].render("Grave", True, config.COLOURS['Player 1'])
        grave_rect = grave_text.get_rect(center=(grave_x + card_width // 2, grave_y + card_height // 2))
        surface.blit(grave_text, grave_rect)

        # Player 2 areas (left side)
        # Draw Add Deck button for Player 2
        add_deck_rect.midtop = (window_width // 2 - 150, middle_y - 40)  # Increased spacing from center
        
        # Draw pulsing effect
        plus_size, plus_offset = self.add_deck_plus_effects['Player 2'].get_state()
        pulse_scaled = pygame.transform.scale(self._cached_scaled_image, 
            (int(scaled_width * (1 + plus_offset[0]/100)), 
             int(scaled_height * (1 + plus_offset[1]/100))))
        surface.blit(pulse_scaled, 
            (add_deck_rect.centerx - pulse_scaled.get_width()//2,
             add_deck_rect.top))
        
        # Draw Player 2 label (upside down)
        player2_text = config.FONTS['text'].render("Player 2", True, config.COLOURS['Player 2'])
        player2_text = pygame.transform.rotate(player2_text, 180)  # Rotate 180 degrees
        player2_rect = player2_text.get_rect()
        player2_rect.midbottom = (grid_x - 30 - card_width // 2, middle_y + 20)  # Just below middle
        surface.blit(player2_text, player2_rect)
        
        # Horizontal card (Atlas) near the middle, slightly above middle line
        atlas_x = grid_x - card_height - 30  # Left of grid + 30px spacing
        atlas_y = middle_y - card_width - 20  # 20px above middle line
        pygame.draw.rect(surface, config.COLOURS['Player 2'], 
                        (atlas_x, atlas_y, card_height, card_width), 2)  # Landscape orientation so card_width is y size
        
        # Draw "Atlas" label (upside down)
        atlas_text = config.FONTS['subtle'].render("Atlas", True, config.COLOURS['Player 2'])
        atlas_text = pygame.transform.rotate(atlas_text, 180)  # Rotate 180 degrees
        atlas_rect = atlas_text.get_rect(center=(atlas_x + card_height // 2, atlas_y + card_width // 2))
        surface.blit(atlas_text, atlas_rect)
        
        # Vertical cards (Deck and Graveyard) above the horizontal card
        deck_x = atlas_x + (card_height - card_width) // 2  # Center under the horizontal card
        deck_y = atlas_y - card_height - 30  # 30px gap
        pygame.draw.rect(surface, config.COLOURS['Player 2'], 
                        (deck_x, deck_y, card_width, card_height), 2)  # Portrait orientation so card_width is x size
        
        # Draw "Spells" label (upside down)
        spells_text = config.FONTS['subtle'].render("Spells", True, config.COLOURS['Player 2'])
        spells_text = pygame.transform.rotate(spells_text, 180)  # Rotate 180 degrees
        spells_rect = spells_text.get_rect(center=(deck_x + card_width // 2, deck_y + card_height // 2))
        surface.blit(spells_text, spells_rect)
        
        grave_x = deck_x
        grave_y = deck_y - card_height - 30  # 30px gap
        pygame.draw.rect(surface, config.COLOURS['Player 2'], 
                        (grave_x, grave_y, card_width, card_height), 2)  # Portrait orientation so card_width is x size
        
        # Draw "Grave" label (upside down)
        grave_text = config.FONTS['subtle'].render("Grave", True, config.COLOURS['Player 2'])
        grave_rect = grave_text.get_rect(center=(grave_x + card_width // 2, grave_y + card_height // 2))
        surface.blit(grave_text, grave_rect)

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
        