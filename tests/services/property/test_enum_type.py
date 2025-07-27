import unittest
from unittest.mock import patch, Mock
from configurator.services.property.enum_type import EnumType
from configurator.services.enumeration_service import Enumerations


class TestEnumType(unittest.TestCase):
    """Test the EnumType class"""

    def test_enum_type_init(self):
        """Test EnumType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "enum",
            "required": True,
            "enums": "test_enum"
        }
        prop = EnumType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "enum")
        self.assertTrue(prop.required)
        self.assertEqual(prop.enums, "test_enum")

    def test_enum_type_to_dict(self):
        """Test EnumType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "enum",
            "required": True,
            "enums": "test_enum"
        }
        prop = EnumType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "enum")
        self.assertTrue(result["required"])
        self.assertEqual(result["enums"], "test_enum")

    def test_enum_type_to_json_schema(self):
        """Test EnumType to_json_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "enum",
            "required": True,
            "enums": "test_enum"
        }
        prop = EnumType(data)
        
        with patch('configurator.services.enumeration_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enum.get_enum_values.return_value = ["value1", "value2"]
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_json_schema(mock_enum)
            
            self.assertEqual(result["type"], "string")
            self.assertEqual(result["enum"], ["value1", "value2"])

    def test_enum_type_to_bson_schema(self):
        """Test EnumType to_bson_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "enum",
            "required": True,
            "enums": "test_enum"
        }
        prop = EnumType(data)
        
        with patch('configurator.services.enumeration_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enum.get_enum_values.return_value = ["value1", "value2"]
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_bson_schema(mock_enum)
            
            self.assertEqual(result["bsonType"], "string")
            self.assertEqual(result["enum"], ["value1", "value2"])


if __name__ == '__main__':
    unittest.main() 