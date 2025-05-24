import pygame
import time
import Util_Config as config


class DebugDisplay:
    """Display debug information on screen."""
    
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock = clock
        self.messages = []
        self.max_messages = 10  # Maximum number of messages to display
        self.message_lifetime = 2.0  # How long messages stay visible (in seconds)
        self.font = pygame.font.SysFont('arial', 12)  # Smaller font size
        self.color = (255, 0, 255)  # Magenta color
        self.fps = 0
        self.fps_update_time = time.time()
        self.fps_update_interval = 0.5  # Update FPS every 0.5 seconds
        
    def add_message(self, message: str) -> None:
        """Add a message to the display."""
        self.messages.append({
            'text': message,
            'time': time.time()
        })
        # Keep only the most recent messages
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
            
    def clear_messages(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        
    def update(self) -> None:
        """Update message lifetimes and FPS."""
        current_time = time.time()
        
        # Update FPS
        if current_time - self.fps_update_time >= self.fps_update_interval:
            self.fps = int(self.clock.get_fps())
            self.fps_update_time = current_time
            
        # Update message lifetimes
        self.messages = [msg for msg in self.messages 
                        if current_time - msg['time'] < self.message_lifetime]
        
    def draw(self) -> None:
        """Draw debug messages on screen."""
        # Always draw FPS first
        fps_text = self.font.render(f"FPS: {self.fps}", True, self.color)
        self.screen.blit(fps_text, (10, 10))
        
        if not self.messages:
            return
            
        # Draw messages below FPS
        y = 25  # Start below FPS
        for msg in self.messages:
            text = self.font.render(msg['text'], True, self.color)
            self.screen.blit(text, (10, y))
            y += 15  # Smaller line spacing 