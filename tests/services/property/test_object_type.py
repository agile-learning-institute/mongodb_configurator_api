import unittest
from unittest.mock import patch, Mock
from configurator.services.property.object_type import ObjectType
from configurator.services.enumeration_service import Enumerations


class TestObjectType(unittest.TestCase):
    """Test the ObjectType class"""

    def test_object_type_init(self):
        """Test ObjectType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "object",
            "required": True,
            "properties": [
                {"name": "prop1", "type": "string"},
                {"name": "prop2", "type": "number"}
            ]
        }
        prop = ObjectType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "object")
        self.assertTrue(prop.required)
        self.assertEqual(len(prop.properties), 2)

    def test_object_type_to_dict(self):
        """Test ObjectType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "object",
            "required": True,
            "properties": [
                {"name": "prop1", "type": "string"},
                {"name": "prop2", "type": "number"}
            ]
        }
        prop = ObjectType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "object")
        self.assertTrue(result["required"])
        self.assertEqual(len(result["properties"]), 2)


if __name__ == '__main__':
    unittest.main() 