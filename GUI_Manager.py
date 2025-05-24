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
from GUI_Main_Window import Main_Window
from Util_Debug import DebugDisplay
from typing import Dict, List, Callable, Any, Set


class GUI_Manager:
    """Manages all GUI panels and their interactions."""
    
    def __init__(self, screen: pygame.Surface = None) -> None:
        """Initialize the GUI manager with optional screen parameter."""
        if screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
            pygame.display.set_caption("Sorcery: The Contested Realm")
        else:
            self.screen = screen
            
        # Event handling
        self.event_subscribers: Dict[pygame.event.EventType, List[Callable[[pygame.event.Event], bool]]] = {}
        self.mouse_subscribers: List[Callable[[int, int], None]] = []
        self.active_components: Set[str] = set()  # Track which components are active
        
        # Initialize other properties
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize components
        self.main_window = Main_Window(self.screen)
        self.debug_display = DebugDisplay(self.screen, self.clock)
        
        # Start with title screen
        self.setup_title_screen()
        
    def setup_title_screen(self) -> None:
        """Set up the title screen and its event handlers."""
        # Clear any existing event handlers
        self.event_subscribers.clear()
        self.mouse_subscribers.clear()
        self.active_components.clear()
        
        # Add title screen event handlers
        self.subscribe_to_event(pygame.QUIT, self.handle_quit)
        self.subscribe_to_event(pygame.KEYDOWN, self.handle_title_keydown)
        self.subscribe_to_event(pygame.MOUSEBUTTONDOWN, self.handle_title_click)
        
        # Start title screen fade in
        self.main_window.start_title_fade_in()
        self.active_components.add('title_screen')
        
    def transition_to_main_menu(self) -> None:
        """Transition from title screen to main menu."""
        # Start title fade out and menu fade in
        self.main_window.start_transition()
        
        # Update event handlers for main menu
        self.event_subscribers.clear()
        self.mouse_subscribers.clear()
        self.active_components.clear()
        
        # Add main menu event handlers
        self.subscribe_to_event(pygame.QUIT, self.handle_quit)
        self.subscribe_to_event(pygame.VIDEORESIZE, self.handle_resize)
        self.subscribe_to_event(pygame.KEYDOWN, self.handle_keydown)
        self.subscribe_to_event(pygame.MOUSEBUTTONDOWN, self.handle_mouse_click)
        self.subscribe_to_event(pygame.MOUSEMOTION, self.handle_mouse_motion)
        
        self.active_components.add('main_menu')
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        # Let main window handle all events first
        if self.main_window.handle_event(event):
            return True
            
        # Pass event to all subscribers for this event type
        if event.type in self.event_subscribers:
            for callback in self.event_subscribers[event.type]:
                if callback(event):
                    return True
                    
        return False
        
    def update(self) -> None:
        """Update GUI state."""
        # Update main window
        self.main_window.update()
        
        # Check for title screen transition completion
        if 'title_screen' in self.active_components and self.main_window.title_fade_complete:
            self.transition_to_main_menu()
            
        # Update debug display
        self.debug_display.update()
        
    def draw(self) -> None:
        """Draw the GUI."""
        # Draw main window
        self.main_window.draw()
        
        # Draw debug display
        if config.IN_DEBUG_MODE:
            self.debug_display.draw()
                
    def subscribe_to_event(self, event_type: pygame.event.EventType, callback: Callable[[pygame.event.Event], bool]) -> None:
        """Subscribe to a specific event type."""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        self.event_subscribers[event_type].append(callback)
        
    def subscribe_to_mouse(self, callback: Callable[[int, int], None]) -> None:
        """Subscribe to mouse position updates."""
        self.mouse_subscribers.append(callback)
        
    def unsubscribe_from_event(self, event_type: pygame.event.EventType, callback: Callable[[pygame.event.Event], bool]) -> None:
        """Unsubscribe from a specific event type."""
        if event_type in self.event_subscribers:
            self.event_subscribers[event_type].remove(callback)
            
    def unsubscribe_from_mouse(self, callback: Callable[[int, int], None]) -> None:
        """Unsubscribe from mouse position updates."""
        if callback in self.mouse_subscribers:
            self.mouse_subscribers.remove(callback)
            
    def handle_events(self) -> None:
        """Handle pygame events using the subscription system."""
        for event in pygame.event.get():
            self.handle_event(event)
                    
    def handle_quit(self, event: pygame.event.Event) -> bool:
        """Handle quit event."""
        self.running = False
        pygame.quit()
        sys.exit()
        return True

    def handle_resize(self, event: pygame.event.Event) -> bool:
        """Handle window resize event."""
        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        return True
            
    def handle_keydown(self, event: pygame.event.Event) -> bool:
        """Handle key press events."""
        if event.key == pygame.K_d:
            config.IN_DEBUG_MODE = not config.IN_DEBUG_MODE
            self.debug_display.add_message(f"Debug Mode: {'Enabled' if config.IN_DEBUG_MODE else 'Disabled'}")
            return True
        elif event.key == pygame.K_p:
            config.IN_PROFILING_MODE = not config.IN_PROFILING_MODE
            self.debug_display.add_message(f"Profiling Mode: {'Enabled' if config.IN_PROFILING_MODE else 'Disabled'}")
            return True
        return False
            
    def handle_title_keydown(self, event: pygame.event.Event) -> bool:
        """Handle key press events during title screen."""
        if event.key == pygame.K_RETURN:
            self.transition_to_main_menu()
            return True
        return False
            
    def handle_title_click(self, event: pygame.event.Event) -> bool:
        """Handle mouse click events during title screen."""
        self.transition_to_main_menu()
        return True
            
    def handle_mouse_click(self, event: pygame.event.Event) -> bool:
        """Handle mouse click events."""
        return False
            
    def handle_mouse_motion(self, event: pygame.event.Event) -> bool:
        """Handle mouse motion events."""
        # Notify all mouse subscribers
        for callback in self.mouse_subscribers:
            callback(event.pos[0], event.pos[1])
        return True

    def run(self) -> None:
        """Main game loop."""
        import cProfile
        import pstats
        import os
        import tempfile
        import traceback
        
        # Initialize profiling if enabled
        pr = None
        profile_file = None
        if config.IN_PROFILING_MODE:
            profile_file = os.path.join(tempfile.gettempdir(), 'sorcery_profile.prof')
            pr = cProfile.Profile()
            pr.enable(subcalls=False, builtins=False)
        
        try:
            while self.running:
                try:
                    if config.IN_PROFILING_MODE and pr is not None:
                        pr.enable(subcalls=False, builtins=False)
                    
                    self.handle_events()
            
                    # Update effects
                    self.main_window.update()
            
                    # Update debug display
                    self.debug_display.update()
                    
                    if config.IN_PROFILING_MODE and pr is not None:
                        pr.disable()
                    
                    # Drawing operations
                    self.draw()
                        
                    pygame.display.flip()
                    self.clock.tick(config.FPS)
                except Exception as e:
                    print("\nError in game loop:")
                    print("Error type:", type(e).__name__)
                    print("Error message:", str(e))
                    print("\nTraceback:")
                    traceback.print_exc()
                    # Don't exit immediately, try to keep running
                    continue
        except Exception as e:
            print("\nFatal error in game:")
            print("Error type:", type(e).__name__)
            print("Error message:", str(e))
            print("\nTraceback:")
            traceback.print_exc()
        finally:
            if config.IN_PROFILING_MODE and pr is not None:
                pr.disable()
                pr.dump_stats(profile_file)
                print("\nProfiling data saved to:", profile_file)
                print("To view the profile visualization, run:")
                print("pip install snakeviz")
                print("snakeviz", profile_file)
            
            pygame.quit()
            sys.exit()
        