'''
Purpose: Defines visual/animated effects for game feel.
Responsibilities:
	•	pulse(obj) - scales object to indicate attention
	•	wiggle(obj) - tilts object subtly for animation
	•	fade(obj) - fade object for available moves
	•	greyscale(obj) - makes object greyscale to show unavailable moves or excluded cards from the action of interest
	•	flip(card) - visually flips a card
	•	tap(card) - rotates card to show tapped state
'''

import math
import pygame
from abc import ABC, abstractmethod
import time
from typing import Any, Tuple


class Effect(ABC):
    """Base class for all visual effects."""
    
    # Shared clock for all effects
    _clock = pygame.time.Clock()
    
    def __init__(self, duration: float = 1.0) -> None:
        """
        Initialize the base effect.
        
        Args:
            duration: If set, the effect will complete in this many seconds.
                     If None, the effect will loop indefinitely.
        """
        self.duration = duration
        self.time = 0.0
        self.is_complete = False
        self.last_update = time.time()
    
    def update(self) -> None:
        """Update the effect's animation state."""
        if self.is_complete:
            return
            
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        self.time += dt
        
        if self.duration is not None:
            if self.time >= self.duration:
                self.time = self.duration  # Keep at final time instead of resetting
                self.is_complete = True
        else:
            if self.time >= 2 * math.pi:
                self.time = 0.0
    
    @abstractmethod
    def get_state(self):
        """Get the current state of the effect."""
        pass
    
    def reset(self) -> None:
        """Reset the effect to its initial state."""
        self.time = 0.0
        self.is_complete = False
        self.last_update = time.time()


class wiggle(Effect):
    def __init__(self, size: tuple[int, int], angle_range: float = 5.0, speed: float = 0.1, 
                 pivot: tuple[float, float] = None, loop: bool = True) -> None:
        """
        Initialize a wiggle effect for rotation animations.
        
        Args:
            size: Tuple of (width, height) for the object size
            angle_range: Maximum rotation angle in degrees (default: 5.0)
            speed: Animation speed (default: 0.1)
            pivot: Optional pivot point (x, y) as percentage of size (0.0-1.0). 
                  If None, uses center (0.5, 0.5)
            loop: Whether to loop the animation (default: True)
                  If False, will stop at the maximum angle
        """
        super().__init__(duration=None if loop else 1.0)  # Duration only used for non-looping
        self.size = size
        self.angle_range = math.radians(angle_range)  # Convert to radians
        self.speed = speed
        self.pivot = pivot if pivot else (0.5, 0.5)  # Default to center
        self.loop = loop
        
    def update(self) -> None:
        """Update the wiggle animation state."""
        dt = Effect._clock.tick() / 1000.0  # Convert to seconds
        self.time += dt * self.speed
        
        if self.loop:
            if self.time >= 2 * math.pi:
                self.time = 0.0
        else:
            # Stop at maximum angle
            if self.time >= math.pi / 2:
                self.time = math.pi / 2
                self.is_complete = True
            
    def get_state(self) -> tuple[float, tuple[int, int]]:
        """
        Get the current rotation angle and pivot point.
        
        Returns:
            Tuple of (rotation_angle, pivot_point)
        """
        rotation = math.degrees(math.sin(self.time) * self.angle_range)
        pivot_point = (
            int(self.size[0] * self.pivot[0]),
            int(self.size[1] * self.pivot[1])
        )
        return rotation, pivot_point


class fade(Effect):
    def __init__(self, start_alpha: int = 0, end_alpha: int = 255, duration: float = 1.0, loop: bool = False) -> None:
        """
        Initialize a fade effect for smooth alpha transitions.
        
        Args:
            start_alpha: Starting alpha value (0-255)
            end_alpha: Target alpha value (0-255)
            duration: Time in seconds for the complete fade (default: 1.0)
            loop: Whether to loop the animation (default: False)
        """
        super().__init__(duration)
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.loop = loop
    
    def update(self) -> None:
        """Update the fade animation state."""
        if self.is_complete:
            return
        
        dt = Effect._clock.tick() / 1000.0  # Convert to seconds
        self.time += dt
        
        if not self.loop:
            if self.time >= self.duration:
                self.time = self.duration  # Keep at final time
                self.is_complete = True
        else:
            if self.time >= self.duration:
                self.time = 0.0
    
    def get_state(self) -> int:
        """
        Get the current alpha value.
        
        Returns:
            Current alpha value (0-255)
        """
        if self.duration == 0:
            return self.end_alpha
        
        progress = self.time / self.duration
        return int(self.start_alpha + (self.end_alpha - self.start_alpha) * progress)


class greyscale(Effect):
    def __init__(self, surface: pygame.Surface, intensity: float = 1.0) -> None:
        """
        Initialize a greyscale effect for a surface.
        
        Args:
            surface: The pygame surface to apply greyscale to
            intensity: Greyscale intensity (0.0-1.0)
        """
        super().__init__()
        self.original_surface = surface.copy()
        self.intensity = max(0.0, min(1.0, intensity))
        self.greyscale_surface = None
        self.update_greyscale()
        
    def update_greyscale(self) -> None:
        """Update the greyscale version of the surface."""
        # Create a copy of the original surface
        self.greyscale_surface = self.original_surface.copy()
        
        # Create a temporary surface for the greyscale effect
        temp_surface = pygame.Surface(self.greyscale_surface.get_size(), pygame.SRCALPHA)
        
        # Apply greyscale effect
        for x in range(self.greyscale_surface.get_width()):
            for y in range(self.greyscale_surface.get_height()):
                color = self.greyscale_surface.get_at((x, y))
                if color.a > 0:  # Only process non-transparent pixels
                    # Calculate greyscale value
                    grey = int(0.299 * color.r + 0.587 * color.g + 0.114 * color.b)
                    # Apply intensity
                    new_color = pygame.Color(
                        int(color.r * (1 - self.intensity) + grey * self.intensity),
                        int(color.g * (1 - self.intensity) + grey * self.intensity),
                        int(color.b * (1 - self.intensity) + grey * self.intensity),
                        color.a
                    )
                    temp_surface.set_at((x, y), new_color)
        
        self.greyscale_surface = temp_surface
        
    def get_state(self) -> pygame.Surface:
        """
        Get the current surface.
        
        Returns:
            The current pygame surface
        """
        return self.greyscale_surface if self.intensity > 0 else self.original_surface


def flip(card):
    print(f"Flip effect on {card}")


class pulse(Effect):
    def __init__(self, size: tuple[int, int], scale_factor: float = 0.1, speed: float = 1.0,
                 loop: bool = True) -> None:
        """
        Initialize a pulse effect for hover animations.
        
        Args:
            size: Tuple of (width, height) for the base size
            scale_factor: How much to scale up/down (default: 0.1 = 10%)
                        Positive = grow first, negative = shrink first
            speed: Animation speed (default: 1.0)
            loop: Whether to loop the animation (default: True)
                  If False, will stop at extreme point (max size if growing, min size if shrinking)
        """
        super().__init__(duration=None if loop else 1.0)  # Duration only used for non-looping
        self.original_size = size
        self.scale_factor = scale_factor
        self.speed = speed
        self.loop = loop
        self.growing = scale_factor > 0  # Track if we're growing or shrinking
        
    def update(self) -> None:
        """Update the pulse animation state."""
        dt = Effect._clock.tick() / 1000.0  # Convert to seconds
        self.time += dt * self.speed
        
        if self.loop:
            if self.time >= 2 * math.pi:
                self.time = 0.0
        else:
            # Stop at extreme point based on direction
            if self.growing and self.time >= math.pi / 2:
                self.time = math.pi / 2
                self.is_complete = True
            elif not self.growing and self.time >= 3 * math.pi / 2:
                self.time = 3 * math.pi / 2
                self.is_complete = True
            
    def get_state(self) -> tuple[tuple[int, int], tuple[float, float]]:
        """
        Get the current scaled size and offset.
        
        Returns:
            Tuple of (scaled_size, offset)
        """
        # Calculate scale based on sine wave
        # Adjust phase based on direction (growing vs shrinking)
        phase = 0 if self.growing else math.pi
        scale = 1.0 + (math.sin(self.time + phase) * abs(self.scale_factor))
        
        # Calculate new size
        new_width = int(self.original_size[0] * scale)
        new_height = int(self.original_size[1] * scale)
        
        # Calculate offset to keep center point
        offset_x = (new_width - self.original_size[0]) / 2
        offset_y = (new_height - self.original_size[1]) / 2
        
        return (new_width, new_height), (offset_x, offset_y)


class tap(Effect):
    def __init__(self, size: tuple[int, int], duration: float = 1.0) -> None:
        """
        Initialize a tap effect that combines rotation and scaling.
        
        Args:
            size: Tuple of (width, height) for the base size
            duration: Time in seconds for the complete animation (default: 1.0)
        """
        super().__init__(duration)
        self.base_size = size
        self.scale_factor = 0.1  # 10% growth
        self.rotation_target = 90  # 90 degrees clockwise
        
    def get_state(self) -> tuple[float, tuple[int, int], tuple[int, int]]:
        """
        Get the current rotation angle, scaled size, and offset.
        
        Returns:
            Tuple of (rotation_angle, scaled_size, offset)
        """
        # Calculate progress (0.0 to 1.0)
        progress = self.time / self.duration
        
        # Use smooth easing function (sine) for both rotation and scale
        ease = math.sin(progress * math.pi / 2)
        
        # Calculate rotation (0 to 90 degrees)
        rotation = self.rotation_target * ease
        
        # Calculate scale (1.0 to 1.1 and back to 1.0)
        scale = 1.0 + (self.scale_factor * math.sin(progress * math.pi))
        
        # Calculate scaled size
        scaled_size = (
            int(self.base_size[0] * scale),
            int(self.base_size[1] * scale)
        )
        
        # Calculate offset to keep centered
        offset = (
            (scaled_size[0] - self.base_size[0]) // 2,
            (scaled_size[1] - self.base_size[1]) // 2
        )
        
        return rotation, scaled_size, offset 


class slide(Effect):
    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int], 
                 duration: float = 1.0, loop: bool = False) -> None:
        """
        Initialize a slide effect for smooth position transitions.
        
        Args:
            start_pos: Starting (x, y) position
            end_pos: Target (x, y) position
            duration: Time in seconds for the complete slide (default: 1.0)
            loop: Whether to loop the animation (default: False)
        """
        super().__init__(duration if not loop else None)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.loop = loop
        
    def update(self) -> None:
        """Update the slide animation state."""
        if self.is_complete:
            return
            
        dt = Effect._clock.tick() / 1000.0  # Convert to seconds
        self.time += dt
        
        if not self.loop:
            if self.time >= self.duration:
                self.time = self.duration  # Keep at final time
                self.is_complete = True
        else:
            if self.time >= self.duration:
                self.time = 0.0
                
    def get_state(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Get the current position and offset.
            
        Returns:
            Tuple of (current_position, offset)
            - current_position: The current (x, y) position
            - offset: The offset from the start position
        """
        if not self.loop and self.is_complete:
            return self.end_pos, (0, 0)
            
        progress = self.time / self.duration
        
        # Use smooth easing function (sine) for natural movement
        ease = math.sin(progress * math.pi / 2)
        
        # Calculate current position
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * ease
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * ease
        
        # Calculate offset from start position
        offset_x = current_x - self.start_pos[0]
        offset_y = current_y - self.start_pos[1]
        
        return (int(current_x), int(current_y)), (int(offset_x), int(offset_y)) 