import unittest
from unittest.mock import patch, Mock
from configurator.services.property.ref_type import RefType
from configurator.services.enumeration_service import Enumerations


class TestRefType(unittest.TestCase):
    """Test the RefType class"""

    def test_ref_type_init(self):
        """Test RefType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "ref",
            "required": True,
            "ref": "test.yaml"
        }
        prop = RefType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "ref")
        self.assertTrue(prop.required)
        self.assertEqual(prop.ref, "test.yaml")

    def test_ref_type_to_dict(self):
        """Test RefType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "ref",
            "required": True,
            "ref": "test.yaml"
        }
        prop = RefType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "ref")
        self.assertTrue(result["required"])
        self.assertEqual(result["ref"], "test.yaml")


if __name__ == '__main__':
    unittest.main() 