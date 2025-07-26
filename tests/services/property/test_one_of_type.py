import unittest
from unittest.mock import patch, Mock
from configurator.services.property.one_of_type import OneOfType
from configurator.services.enumerator_service import Enumerations


class TestOneOfType(unittest.TestCase):
    """Test the OneOfType class"""

    def test_one_of_type_init(self):
        """Test OneOfType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "one_of",
            "required": True,
            "properties": [
                {"name": "option1", "type": "string"},
                {"name": "option2", "type": "number"}
            ]
        }
        prop = OneOfType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "one_of")
        self.assertTrue(prop.required)
        self.assertEqual(len(prop.properties), 2)

    def test_one_of_type_to_dict(self):
        """Test OneOfType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "one_of",
            "required": True,
            "properties": [
                {"name": "option1", "type": "string"},
                {"name": "option2", "type": "number"}
            ]
        }
        prop = OneOfType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "one_of")
        self.assertTrue(result["required"])
        self.assertEqual(len(result["properties"]), 2)


if __name__ == '__main__':
    unittest.main() 