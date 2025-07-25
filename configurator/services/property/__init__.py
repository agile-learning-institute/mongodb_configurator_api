"""
Services package
"""

from .property import create_property

# Alias for backward compatibility
Property = create_property

__all__ = ['Property', 'create_property']
