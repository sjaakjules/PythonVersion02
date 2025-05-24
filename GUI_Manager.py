'''
Purpose: Manages user interface input and visual feedback.
Responsibilities:
 •	Monitors cursor hover, click, drag, and tap interactions.
 •	Shows visual cues (highlighting legal moves, mana costs, ability activation).
 •	Updates the display when cards are played, tapped, moved, flipped.
 •	Calls Util_Effects.py to animate the cards, tokens, hands and tapping etc.
'''

import pygame
import Util_Config as config
import sys
import traceback
from GUI_Main_Window import Main_Window
from GUI_Splash_Screen import Splash_Screen
from Util_Debug import Debug_Display
from typing import Dict, List, Callable, Any, Set
import time


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
        # self.mouse_subscribers: List[Callable[[int, int], None]] = []
        # self.active_components: Set[str] = set()  # Track which components are active
        
        # Initialize other properties
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize components
        self.splash_screen = Splash_Screen(self.screen, self)
        self.main_window: Main_Window | None = None
        self.debug_display = Debug_Display(self.screen, self.clock)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        # Handle quit event
        if self.handle_quit(event):
            return True
        
        if self.handle_resize(event):
            return True
        
        # Pass event to all subscribers for this event type
        if event.type in self.event_subscribers:
            for callback in self.event_subscribers[event.type]:
                if callback(event):
                    return True  # ToDo: Check if this should reutrn on first true callback or keep going through all subscribed events.
                    
        return False
        
    def update(self) -> None:
        """Update GUI state."""
        # update splash screen
        if not self.splash_screen.update():
            # Update main window
            if self.main_window is None:
                self.main_window = Main_Window(self.screen, self)
            self.main_window.update()
            
        # Update debug display
        self.debug_display.update()
        
    def draw(self) -> None:
        """Draw the GUI."""
        # Draw splash screen
        if not self.splash_screen.draw():
            # Update main window
            self.main_window.draw()
        # Draw debug display
        self.debug_display.draw()
                
    def subscribe_to_event(self, event_type: pygame.event.EventType, callback: Callable[[pygame.event.Event], bool]) -> None:
        """Subscribe to a specific event type."""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        self.event_subscribers[event_type].append(callback)
        
    def unsubscribe_from_event(self, event_type: pygame.event.EventType, callback: Callable[[pygame.event.Event], bool]) -> None:
        """Unsubscribe from a specific event type."""
        if event_type in self.event_subscribers:
            self.event_subscribers[event_type].remove(callback)
            
    def handle_events(self) -> None:
        """Handle pygame events using the subscription system."""
        for event in pygame.event.get():
            self.handle_event(event)
                    
    def handle_quit(self, event: pygame.event.Event) -> bool:
        """Handle quit event."""
        
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            sys.exit()
            return True
        return False

    def handle_resize(self, event: pygame.event.Event) -> bool:
        """Handle window resize event."""
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            return True
        return False
            
    def run(self) -> None:
        """Main game loop."""
        pr = None
        profile_file = None
        
        if config.IN_PROFILING_MODE:
            import cProfile
            import pstats
            import os
            import tempfile
        
            # Initialize profiling if enabled
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
                    self.update()
                    
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
                    time.sleep(1)  # Give time to read the error
                    # Don't exit immediately, try to keep running
                    continue
        except Exception as e:
            print("\nFatal error in game:")
            print("Error type:", type(e).__name__)
            print("Error message:", str(e))
            print("\nTraceback:")
            traceback.print_exc()
            time.sleep(1)  # Give time to read the error
        finally:
            if config.IN_PROFILING_MODE and pr is not None:
                pr.disable()
                pr.dump_stats(profile_file)
                print("\nProfiling data saved to:", profile_file)
                print("To view the profile visualization, run:")
                print("pip install snakeviz")
                print("snakeviz", profile_file)
            
            print("\nShutting down...")
            pygame.quit()
            time.sleep(0.5)  # Give time for final messages to print
            sys.exit()
        