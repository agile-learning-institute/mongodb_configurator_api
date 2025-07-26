import unittest
from unittest.mock import patch, Mock
from configurator.services.property.enum_array_type import EnumArrayType
from configurator.services.enumerator_service import Enumerations


class TestEnumArrayType(unittest.TestCase):
    """Test the EnumArrayType class"""

    def test_enum_array_type_init(self):
        """Test EnumArrayType initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "enum_array",
            "required": True,
            "enums": "test_enum"
        }
        prop = EnumArrayType(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "enum_array")
        self.assertTrue(prop.required)
        self.assertEqual(prop.enums, "test_enum")

    def test_enum_array_type_to_dict(self):
        """Test EnumArrayType to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "enum_array",
            "required": True,
            "enums": "test_enum"
        }
        prop = EnumArrayType(data)
        result = prop.to_dict()
        
        self.assertEqual(result["name"], "test_prop")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["type"], "enum_array")
        self.assertTrue(result["required"])
        self.assertEqual(result["enums"], "test_enum")

    def test_enum_array_type_to_json_schema(self):
        """Test EnumArrayType to_json_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "enum_array",
            "required": True,
            "enums": "test_enum"
        }
        prop = EnumArrayType(data)
        
        with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enum.get_enum_values.return_value = ["value1", "value2"]
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_json_schema(mock_enum)
            
            self.assertEqual(result["type"], "array")
            self.assertEqual(result["items"]["type"], "string")
            self.assertEqual(result["items"]["enum"], ["value1", "value2"])

    def test_enum_array_type_to_bson_schema(self):
        """Test EnumArrayType to_bson_schema method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "enum_array",
            "required": True,
            "enums": "test_enum"
        }
        prop = EnumArrayType(data)
        
        with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enum.get_enum_values.return_value = ["value1", "value2"]
            mock_enumerations.return_value = mock_enum
            
            result = prop.to_bson_schema(mock_enum)
            
            self.assertEqual(result["bsonType"], "array")
            self.assertEqual(result["items"]["bsonType"], "string")
            self.assertEqual(result["items"]["enum"], ["value1", "value2"])


if __name__ == '__main__':
    unittest.main() 