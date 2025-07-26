import unittest
from unittest.mock import patch, Mock
from configurator.services.property.complex_type import ComplexType
from configurator.services.enumeration_service import Enumerations


class TestComplexType(unittest.TestCase):
    """Test the ComplexType class"""

    def test_complex_type_init(self):
        """Test ComplexType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "complex",
            "required": True,
            "json_type": {"type": "string", "pattern": "^[a-z]+$"},
            "bson_type": {"bsonType": "string", "pattern": "^[a-z]+$"}
        }
        prop = ComplexType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "complex")
        self.assertTrue(prop.required)
        self.assertEqual(prop.json_type, {"type": "string", "pattern": "^[a-z]+$"})
        self.assertEqual(prop.bson_type, {"bsonType": "string", "pattern": "^[a-z]+$"})

    def test_complex_type_to_dict(self):
        """Test ComplexType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "complex",
            "required": True,
            "json_type": {"type": "string", "pattern": "^[a-z]+$"},
            "bson_type": {"bsonType": "string", "pattern": "^[a-z]+$"}
        }
        prop = ComplexType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "complex")
        self.assertTrue(result["required"])
        self.assertEqual(result["json_type"], {"type": "string", "pattern": "^[a-z]+$"})
        self.assertEqual(result["bson_type"], {"bsonType": "string", "pattern": "^[a-z]+$"})

    def test_complex_type_to_json_schema(self):
        """Test ComplexType to_json_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "complex",
            "required": True,
            "json_type": {"type": "string", "pattern": "^[a-z]+$"}
        }
        prop = ComplexType(data)
        
        with patch('configurator.services.enumeration_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_json_schema(mock_enum)
            
            self.assertEqual(result["type"], "string")
            self.assertEqual(result["pattern"], "^[a-z]+$")

    def test_complex_type_to_bson_schema(self):
        """Test ComplexType to_bson_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "complex",
            "required": True,
            "bson_type": {"bsonType": "string", "pattern": "^[a-z]+$"}
        }
        prop = ComplexType(data)
        
        with patch('configurator.services.enumeration_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_bson_schema(mock_enum)
            
            self.assertEqual(result["bsonType"], "string")
            self.assertEqual(result["pattern"], "^[a-z]+$")


if __name__ == '__main__':
    unittest.main() 