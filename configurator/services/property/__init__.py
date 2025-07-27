"""
Property module - Polymorphic property types for schema generation

This module provides a factory pattern for creating different property types
based on the 'type' field in the input data.

Usage:
    from configurator.services.property import Property
    
    # Create a property (factory will choose appropriate type)
    prop = Property(data)
"""

from .property import Property
from .base import BaseProperty

# Export the main interface
__all__ = ['Property', 'BaseProperty']
