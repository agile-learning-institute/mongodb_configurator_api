import unittest
from unittest.mock import patch, Mock
from configurator.services.property.base import BaseProperty
from configurator.services.enumeration_service import Enumerations
from configurator.utils.configurator_exception import ConfiguratorException


class TestBaseProperty(unittest.TestCase):
    """Test the BaseProperty class"""

    def test_base_property_init(self):
        """Test BaseProperty initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "string",
            "required": True
        }
        prop = BaseProperty(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "string")
        self.assertTrue(prop.required)

    def test_base_property_init_defaults(self):
        """Test BaseProperty initialization with defaults"""
        data = {
            "name": "test_prop",
            "type": "string"
        }
        prop = BaseProperty(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.type, "string")
        self.assertFalse(prop.required)
        self.assertEqual(prop.description, "")

    def test_base_property_missing_name(self):
        """Test BaseProperty raises exception for missing name"""
        data = {
            "type": "string",
            "description": "Test description"
        }
        with self.assertRaises(ConfiguratorException) as context:
            BaseProperty(data)
        self.assertIn("Missing required name", str(context.exception))

    def test_base_property_to_dict(self):
        """Test BaseProperty to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "string",
            "required": True
        }
        prop = BaseProperty(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "string")
        self.assertTrue(result["required"])

    def test_base_property_to_json_schema(self):
        """Test BaseProperty to_json_schema method"""
        data = {"name": "test_prop", "type": "string"}
        prop = BaseProperty(data)
        result = prop.to_json_schema(None)
        self.assertEqual(result["type"], "string")

    def test_base_property_to_bson_schema(self):
        """Test BaseProperty to_bson_schema method"""
        data = {"name": "test_prop", "type": "string"}
        prop = BaseProperty(data)
        result = prop.to_bson_schema(None)
        self.assertEqual(result["bsonType"], "string")


if __name__ == '__main__':
    unittest.main() 