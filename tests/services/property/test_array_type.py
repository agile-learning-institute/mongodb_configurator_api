import unittest
from unittest.mock import patch, Mock
from configurator.services.property.array_type import ArrayType
from configurator.services.enumeration_service import Enumerations


class TestArrayType(unittest.TestCase):
    """Test the ArrayType class"""

    def test_array_type_init(self):
        """Test ArrayType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "array",
            "required": True,
            "items": {"name": "item", "type": "string"}
        }
        prop = ArrayType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "array")
        self.assertTrue(prop.required)
        self.assertIsNotNone(prop.items)

    def test_array_type_to_dict(self):
        """Test ArrayType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "array",
            "required": True,
            "items": {"name": "item", "type": "string"}
        }
        prop = ArrayType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "array")
        self.assertTrue(result["required"])
        self.assertIn("items", result)

    def test_array_type_with_items_missing_name(self):
        """Test ArrayType initialization with items missing name - should default to 'items'"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "array",
            "required": True,
            "items": {"type": "string"}  # Missing name
        }
        prop = ArrayType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertIsNotNone(prop.items)
        # The items property should have a default name of "items"
        self.assertEqual(prop.items.name, "items")
        self.assertEqual(prop.items.type, "string")

    def test_array_type_with_empty_items(self):
        """Test ArrayType initialization with empty items dict - should default name to 'items'"""
        data = {
            "name": "test_prop",
            "type": "array",
            "items": {}  # Empty dict, missing name
        }
        prop = ArrayType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertIsNotNone(prop.items)
        # The items property should have a default name of "items"
        self.assertEqual(prop.items.name, "items")


if __name__ == '__main__':
    unittest.main() 