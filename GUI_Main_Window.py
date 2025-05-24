import pygame
import Util_Effects
import Util_Config as config

class Main_Window:
    # Fade effect settings
    FADE_SETTINGS = {
        'title_fade_in': {
            'start_alpha': 0,
            'end_alpha': 255,
            'duration': 2.0,
            'loop': False
        },
        'title_fade_out': {
            'start_alpha': 255,
            'end_alpha': 0,
            'duration': 0.5,
            'loop': False
        },
        'background_fade_in': {
            'start_alpha': 0,
            'end_alpha': 255,
            'duration': 0.5,
            'loop': False
        },
        'button_pulse': {
            'scale_factor': 0.1,  # 10% scale
            'speed': 2.0  # Faster pulse
        }
    }
    
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        # Title fade in effect
        self.title_fade = Util_Effects.fade(**self.FADE_SETTINGS['title_fade_in'])
        # Background fade in effect (starts at 0, will be triggered after title)
        self.background_fade = Util_Effects.fade(**self.FADE_SETTINGS['background_fade_in'])
        
        # Preload and cache images
        self.title_image = pygame.image.load('assets/Icons/Sorcery Title.png').convert_alpha()
        self.title_rect = self.title_image.get_rect(center=(1920 // 2, int(1080 // 2)))
        
        # Preload background image and cache it
        self.background_image = pygame.image.load('assets/Icons/Sorcery_Screen.png').convert()
        self.background_rect = self.background_image.get_rect()
        
        # Pre-calculate scaled background for different window sizes
        self.scaled_backgrounds = {}
        self.update_scaled_backgrounds()
        
        self.showing_title = True  # Start with title phase
        self.transitioning = False  # Track if we're in transition between phases
        self.transition_complete = False  # Track if transition is complete
        
        # Menu state
        self.showing_menu = False
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
        
        # Update button positions and initialize pulse effects
        self.update_menu_button_positions()
        
    def update_scaled_backgrounds(self) -> None:
        """Pre-calculate scaled backgrounds for common window sizes."""
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate scale for current window size
        scale = min(
            window_width / self.background_rect.width,
            window_height / self.background_rect.height
        )
        scaled_width = int(self.background_rect.width * scale)
        scaled_height = int(self.background_rect.height * scale)
        
        # Cache the scaled background
        self.scaled_backgrounds[(scaled_width, scaled_height)] = pygame.transform.scale(
            self.background_image, 
            (scaled_width, scaled_height)
        )
        
    def get_scaled_background(self, window_width: int, window_height: int) -> pygame.Surface:
        """Get or create a scaled background for the given window size."""
        # Calculate scale for current window size
        scale = min(
            window_width / self.background_rect.width,
            window_height / self.background_rect.height
        )
        scaled_width = int(self.background_rect.width * scale)
        scaled_height = int(self.background_rect.height * scale)
        
        # Check if we have this size cached
        if (scaled_width, scaled_height) not in self.scaled_backgrounds:
            # Create and cache new scaled background
            self.scaled_backgrounds[(scaled_width, scaled_height)] = pygame.transform.scale(
                self.background_image, 
                (scaled_width, scaled_height)
            )
            
        return self.scaled_backgrounds[(scaled_width, scaled_height)]
        
    def start_transition(self) -> None:
        """Start the transition from title to background."""
        if not self.transitioning:  # Only start transition if not already transitioning
            self.showing_title = False
            self.transitioning = True
            # Reset title fade to fade out
            self.title_fade = Util_Effects.fade(**self.FADE_SETTINGS['title_fade_out'])
            # Start background fade in
            self.background_fade = Util_Effects.fade(**self.FADE_SETTINGS['background_fade_in'])
            
    def update(self) -> None:
        """Update window effects."""
        if self.showing_title:
            self.title_fade.update()
        elif self.transitioning:
            self.title_fade.update()
            self.background_fade.update()
            # Check if transition is complete
            if self.title_fade.get_state() <= 0 and self.background_fade.get_state() >= 255:
                self.transitioning = False
                self.transition_complete = True
                
    def draw(self) -> None:
        """Draw the main window with all its elements."""
        # Fill with black
        self.screen.fill((0, 0, 0))
        
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Draw background if we're past the title phase
        if not self.showing_title:
            # Get pre-scaled background
            scaled_bg = self.get_scaled_background(window_width, window_height)
            
            # Center the background
            bg_x = (window_width - scaled_bg.get_width()) // 2
            bg_y = (window_height - scaled_bg.get_height()) // 2
            
            # Apply fade effect to background during transition
            if self.transitioning:
                scaled_bg.set_alpha(self.background_fade.get_state())
            else:
                scaled_bg.set_alpha(255)  # Fully visible after transition
            
            # Draw the background
            self.screen.blit(scaled_bg, (bg_x, bg_y))
        
        # Draw title if we're in title phase or transitioning
        if self.showing_title or self.transitioning:
            # Get current fade alpha from effect
            alpha = self.title_fade.get_state()
            
            # Create a copy of the title image with current alpha
            title_surface = self.title_image.copy()
            title_surface.set_alpha(alpha)
            
            # Draw the title
            self.screen.blit(title_surface, self.title_rect)
            
            # Draw "Press Enter or Click to Start" text if fade is complete and in title phase
            if self.showing_title and alpha >= 255:
                start_text = config.FONTS['subtitle'].render("Press Enter or Click to Start", True, (200, 200, 200))
                text_rect = start_text.get_rect(center=(window_width // 2, int(window_height * 0.9)))
                self.screen.blit(start_text, text_rect)

    def update_menu_button_positions(self) -> None:
        """Update the positions of menu buttons based on screen size."""
        window_width = self.screen.get_width()
        window_height = self.screen.get_height()
        
        # Calculate button size (1/10th of screen height)
        target_height = window_height // 10
        
        # Center positions
        center_x = window_width // 2
        center_y = window_height // 2
        
        # Scale all button images to target height while maintaining aspect ratio
        for button_id, button in self.menu_buttons.items():
            img = button['image']
            aspect_ratio = img.get_width() / img.get_height()
            new_width = int(target_height * aspect_ratio)
            button['image'] = pygame.transform.scale(img, (new_width, target_height))
            
            # Initialize pulse effect with the scaled size
            button['pulse'] = Util_Effects.pulse(
                size=(new_width, target_height),
                **self.FADE_SETTINGS['button_pulse']
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
                
    def handle_menu_click(self, event: pygame.event.Event) -> bool:
        """Handle menu button clicks and return True if a panel should be shown."""
        if not self.showing_menu:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.clicked_button == 'add_board':
                self.showing_menu = False
                return True, 'board'
            elif self.clicked_button in ['add_deck_p1', 'add_deck_p2']:
                self.showing_menu = False
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
        if event.type == pygame.MOUSEBUTTONDOWN and self.showing_title:
            # Handle click on start screen
            self.start_transition()
            return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.showing_title:
            # Handle Enter key on start screen
            self.start_transition()
            return True
        elif event.type == pygame.MOUSEMOTION:
            # Handle mouse motion for hover effects
            if not self.showing_title and self.transition_complete:
                return self.handle_menu_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle menu button clicks
            if self.showing_menu:
                should_show_panel, panel_type = self.handle_menu_click(event)
                if should_show_panel:
                    return True
        return False 