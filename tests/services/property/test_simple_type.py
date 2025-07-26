import unittest
from unittest.mock import patch, Mock
from configurator.services.property.simple_type import SimpleType
from configurator.services.enumerator_service import Enumerations


class TestSimpleType(unittest.TestCase):
    """Test the SimpleType class"""

    def test_simple_type_init(self):
        """Test SimpleType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "simple",
            "required": True,
            "schema": {"type": "string", "format": "email"}
        }
        prop = SimpleType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "simple")
        self.assertTrue(prop.required)
        self.assertEqual(prop.schema, {"type": "string", "format": "email"})

    def test_simple_type_to_dict(self):
        """Test SimpleType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "simple",
            "required": True,
            "schema": {"type": "string", "format": "email"}
        }
        prop = SimpleType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "simple")
        self.assertTrue(result["required"])
        self.assertEqual(result["schema"], {"type": "string", "format": "email"})

    def test_simple_type_to_json_schema(self):
        """Test SimpleType to_json_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "simple",
            "required": True,
            "schema": {"type": "string", "format": "email"}
        }
        prop = SimpleType(data)
        
        with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_json_schema(mock_enum)
            
            self.assertEqual(result["type"], "string")
            self.assertEqual(result["format"], "email")

    def test_simple_type_to_bson_schema(self):
        """Test SimpleType to_bson_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "simple",
            "required": True,
            "schema": {"type": "string", "format": "email"}
        }
        prop = SimpleType(data)
        
        with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_bson_schema(mock_enum)
            
            self.assertEqual(result["bsonType"], "simple")
            self.assertEqual(result["format"], "email")


if __name__ == '__main__':
    unittest.main() 