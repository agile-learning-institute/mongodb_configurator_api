import unittest
from unittest.mock import patch, Mock
from configurator.services.property.custom_type import CustomType
from configurator.services.enumeration_service import Enumerations


class TestCustomType(unittest.TestCase):
    """Test the CustomType class"""

    def test_custom_type_init(self):
        """Test CustomType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "custom_type",
            "required": True
        }
        prop = CustomType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "custom_type")
        self.assertTrue(prop.required)

    def test_custom_type_to_dict(self):
        """Test CustomType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "custom_type",
            "required": True
        }
        prop = CustomType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "custom_type")
        self.assertTrue(result["required"])


if __name__ == '__main__':
    unittest.main() 