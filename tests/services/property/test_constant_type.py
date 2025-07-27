import unittest
from unittest.mock import patch, Mock
from configurator.services.property.constant_type import ConstantType
from configurator.services.enumeration_service import Enumerations


class TestConstantType(unittest.TestCase):
    """Test the ConstantType class"""

    def test_constant_type_init(self):
        """Test ConstantType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "constant",
            "required": True,
            "constant": "test_value"
        }
        prop = ConstantType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "constant")
        self.assertTrue(prop.required)
        self.assertEqual(prop.constant, "test_value")

    def test_constant_type_to_dict(self):
        """Test ConstantType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "constant",
            "required": True,
            "constant": "test_value"
        }
        prop = ConstantType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "constant")
        self.assertTrue(result["required"])
        self.assertEqual(result["constant"], "test_value")

    def test_constant_type_to_json_schema(self):
        """Test ConstantType to_json_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "constant",
            "required": True,
            "constant": "test_value"
        }
        prop = ConstantType(data)
        
        with patch('configurator.services.enumeration_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_json_schema(mock_enum)
            
            self.assertEqual(result["type"], "string")
            self.assertEqual(result["const"], "test_value")

    def test_constant_type_to_bson_schema(self):
        """Test ConstantType to_bson_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "constant",
            "required": True,
            "constant": "test_value"
        }
        prop = ConstantType(data)
        
        with patch('configurator.services.enumeration_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_bson_schema(mock_enum)
            
            self.assertEqual(result["bsonType"], "string")
            self.assertEqual(result["const"], "test_value")

    def test_constant_type_init_defaults(self):
        """Test ConstantType initialization with defaults"""
        data = {
            "name": "test_prop",
            "type": "constant"
        }
        prop = ConstantType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.type, "constant")
        self.assertFalse(prop.required)
        self.assertEqual(prop.constant, "")


if __name__ == '__main__':
    unittest.main() 