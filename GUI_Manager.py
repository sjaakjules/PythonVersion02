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
from GUI_Panel import Panel
from GUI_Panel_Board_Selection import pBoard_Selection
from GUI_Panel_Deck_Selection import pDeck_Selection
from GUI_Main_Window import Main_Window
from Util_Debug import DebugDisplay
from typing import Dict, List, Callable, Any


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
            
        self.panels: Dict[str, Panel] = {}
        self.active_panel: Panel | None = None
        self.event_subscribers: Dict[pygame.event.EventType, List[Callable[[pygame.event.Event], bool]]] = {}
        self.mouse_subscribers: List[Callable[[int, int], None]] = []
        self.debug_text = "Debug Mode: ON"
        
        # Initialize other properties
        self.clock = pygame.time.Clock()
        self.running = True
        self.hover_index = -1
        self.hover_effect = None
        self.selected_board = None
        self.scroll_x = 0
        self.showing_start_screen = True  # Initialize start screen state
        self.showing_deck_selection = False  # Initialize deck selection state
        
        # Initialize main window
        self.main_window = Main_Window(self.screen)
        
        # Initialize panels
        self.board_panel = pBoard_Selection(self.screen)
        self.deck_panel = pDeck_Selection(self.screen)
        self.active_panel = None  # Don't set active panel by default
        self.board_panel.hide()  # Hide the board selection panel by default
        self.deck_panel.hide()   # Hide the deck selection panel by default
        
        # Initialize debug display
        self.debug_display = DebugDisplay(self.screen, self.clock)
        
        # Set up initial event subscriptions
        self.setup_event_subscriptions()
        
    def setup_event_subscriptions(self) -> None:
        """Set up initial event subscriptions."""
        # Always handle these events
        self.subscribe_to_event(pygame.QUIT, self.handle_quit)
        self.subscribe_to_event(pygame.VIDEORESIZE, self.handle_resize)
        self.subscribe_to_event(pygame.KEYDOWN, self.handle_keydown)
        
        # Mouse events
        self.subscribe_to_event(pygame.MOUSEBUTTONDOWN, self.handle_mouse_click)
        self.subscribe_to_event(pygame.MOUSEMOTION, self.handle_mouse_motion)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        # Let main window handle all events first
        if self.main_window.handle_event(event):
            # If main window handled a menu click
            if event.type == pygame.MOUSEBUTTONDOWN and self.main_window.showing_menu:
                should_show_panel, panel_type = self.main_window.handle_menu_click(event)
                if should_show_panel:
                    if panel_type == 'board':
                        self.board_panel.show()
                        self.active_panel = self.board_panel
                    elif panel_type == 'deck':
                        self.deck_panel.show()
                        self.active_panel = self.deck_panel
            return True
            
        # Handle panel events
        if self.active_panel and self.active_panel.handle_event(event):
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
        
        # Check if we should show menu after title transition
        if self.main_window.transition_complete and not self.main_window.showing_menu:
            self.main_window.showing_menu = True
            
        # Update active panel
        if self.active_panel:
            self.active_panel.update()
            
        # Update debug display
        self.debug_display.update()
        
    def draw(self) -> None:
        """Draw the GUI."""
        # Draw main window
        self.main_window.draw()
        
        # Draw menu if active
        self.main_window.draw_menu()
        
        # Draw active panel
        if self.active_panel:
            self.active_panel.draw()
            
        # Draw debug display
        if config.IN_DEBUG_MODE:
            self.debug_display.draw()

    def register_panel(self, name: str, panel: Panel) -> None:
        """Register a panel with the manager."""
        self.panels[name] = panel
        
    def show_panel(self, name: str) -> None:
        """Show a specific panel and hide others."""
        if name in self.panels:
            # Hide current panel if any
            if self.active_panel:
                self.active_panel.hide()
            
            # Show new panel
            self.active_panel = self.panels[name]
            self.active_panel.show()
            
    def hide_panel(self, name: str) -> None:
        """Hide a specific panel."""
        if name in self.panels:
            self.panels[name].hide()
            if self.active_panel == self.panels[name]:
                self.active_panel = None
                
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
            
    def get_panel(self, name: str) -> Panel | None:
        """Get a panel by name."""
        return self.panels.get(name)
        
    def is_panel_visible(self, name: str) -> bool:
        """Check if a panel is visible."""
        panel = self.get_panel(name)
        return panel is not None and panel.is_visible
        
    def get_active_panel(self) -> Panel | None:
        """Get the currently active panel."""
        return self.active_panel

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
        if self.active_panel:
            self.active_panel.update_surface()
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
        elif event.key == pygame.K_RETURN and self.showing_start_screen:
            self.showing_start_screen = False
            self.main_window.start_transition()
            self.main_window.showing_menu = True
            return True
        return False
            
    def handle_mouse_click(self, event: pygame.event.Event) -> bool:
        """Handle mouse click events."""
        if self.showing_start_screen:
            self.showing_start_screen = False
            self.main_window.start_transition()
            self.main_window.showing_menu = True
            return True
            
        if self.active_panel:
            if self.active_panel.handle_event(event):
                if isinstance(self.active_panel, pBoard_Selection):
                    self.selected_board = self.active_panel.selected_board
                    if self.selected_board:
                        self.active_panel.hide()
                        self.debug_display.add_message(f"Selected board: {self.selected_board['artist']}")
                        self.showing_deck_selection = True
                    else:
                        print("No board selected")
                return True
                
        if self.selected_board:
            if event.button == 4:  # Scroll up
                self.scroll_x = max(0, self.scroll_x - 50)
                return True
            elif event.button == 5:  # Scroll down
                self.scroll_x += 50
                return True
                
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
                    if self.active_panel:
                        self.active_panel.update()
            
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
        