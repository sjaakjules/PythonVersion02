'''
Purpose: Factory system for creating visual effects based on settings.
Responsibilities:
    • Create effects based on type and settings
    • Handle default values for effect parameters
    • Support multiple effect types (fade, pulse, slide, etc.)
'''

import Util_Effects
from typing import Dict, Any, Optional, Tuple


class EffectFactory:
    """Factory for creating visual effects based on settings."""
    
    # Default settings for each effect type
    DEFAULT_SETTINGS = {
        'fade': {
            'start_alpha': 0,
            'end_alpha': 255,
            'duration': 1.0,
            'loop': False
        },
        'pulse': {
            'scale_factor': 0.1,  # Positive = grow first, negative = shrink first
            'speed': 1.0,
            'loop': True  # Whether to loop the animation
        },
        'slide': {
            'start_pos': (0, 0),
            'end_pos': (0, 0),
            'duration': 1.0,
            'loop': False
        },
        'wiggle': {
            'angle_range': 5.0,
            'speed': 0.1,
            'pivot': (0.5, 0.5),
            'loop': True  # Whether to loop the animation
        }
    }
    
    @classmethod
    def create_effect(cls, effect_type: str, settings: Dict[str, Any], **kwargs) -> Any:
        """
        Create an effect based on type and settings.
        
        Args:
            effect_type: Type of effect ('fade', 'pulse', 'slide', 'wiggle')
            settings: Dictionary of effect settings
            **kwargs: Additional parameters required by specific effects
            
        Returns:
            The created effect instance
        """
        # Get default settings for this effect type
        default_settings = cls.DEFAULT_SETTINGS.get(effect_type, {})
        
        # Merge default settings with provided settings
        merged_settings = {**default_settings, **settings}
        
        # Create effect based on type
        if effect_type == 'fade':
            return Util_Effects.fade(**merged_settings)
        elif effect_type == 'pulse':
            if 'size' not in kwargs:
                raise ValueError("Pulse effect requires 'size' parameter")
            # Handle pulse-specific settings
            scale_factor = merged_settings.pop('scale_factor', 0.1)
            speed = merged_settings.pop('speed', 1.0)
            loop = merged_settings.pop('loop', True)
            
            # Create pulse effect with custom parameters
            return Util_Effects.pulse(
                size=kwargs['size'],
                scale_factor=scale_factor,
                speed=speed,
                loop=loop
            )
        elif effect_type == 'slide':
            return Util_Effects.slide(**merged_settings)
        elif effect_type == 'wiggle':
            if 'size' not in kwargs:
                raise ValueError("Wiggle effect requires 'size' parameter")
            return Util_Effects.wiggle(size=kwargs['size'], **merged_settings)
        else:
            raise ValueError(f"Unknown effect type: {effect_type}")
            
    @classmethod
    def create_effect_from_config(cls, config: Dict[str, Any], **kwargs) -> Any:
        """
        Create an effect from a configuration dictionary.
        
        Args:
            config: Dictionary containing effect type and settings
                   Format: {'type': 'effect_type', 'settings': {...}}
            **kwargs: Additional parameters required by specific effects
            
        Returns:
            The created effect instance
        """
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
            
        effect_type = config.get('type')
        if not effect_type:
            raise ValueError("Config must specify effect type")
            
        settings = config.get('settings', {})
        return cls.create_effect(effect_type, settings, **kwargs) 