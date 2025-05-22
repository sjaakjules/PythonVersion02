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


def wiggle(obj):
    print(f"Wiggle effect on {obj}")


def fade(obj):
    print(f"Fade effect on {obj}")


def greyscale(obj):
    print(f"Greyscale effect on {obj}")


def flip(card):
    print(f"Flip effect on {card}")


def tap(card):
    print(f"Tap effect on {card}")
    
    
class pulse:
    def __init__(self, base_size, animation_speed=3, scale_factor=0.05):
        self.base_size = base_size
        self.animation_speed = animation_speed
        self.scale_factor = scale_factor
        self.time = 0

    def update(self):
        """Update the animation time."""
        self.time += 0.1

    def get_scale(self):
        """Calculate the current scale factor for the hover effect."""
        return 1.0 + self.scale_factor * math.sin(self.time * self.animation_speed)

    def get_scaled_size(self):
        """Get the current scaled size based on the animation."""
        scale = self.get_scale()
        return (
            int(self.base_size[0] * scale),
            int(self.base_size[1] * scale)
        )

    def get_offset(self, scaled_size):
        """Calculate the offset needed to center the scaled image."""
        return (
            (scaled_size[0] - self.base_size[0]) // 2,
            (scaled_size[1] - self.base_size[1]) // 2
        ) 