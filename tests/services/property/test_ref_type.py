import unittest
from unittest.mock import patch, Mock, MagicMock
from configurator.services.property.ref_type import RefType
from configurator.services.enumeration_service import Enumerations
from configurator.services.dictionary_services import Dictionary
from configurator.utils.configurator_exception import ConfiguratorException


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

    def test_get_dictionary_filename_with_yaml_extension(self):
        """Test that refs with .yaml extension are used as-is"""
        data = {
            "name": "test_prop",
            "type": "ref",
            "ref": "test.yaml"
        }
        prop = RefType(data)
        filename = prop._get_dictionary_filename()
        self.assertEqual(filename, "test.yaml")

    def test_get_dictionary_filename_with_json_extension(self):
        """Test that refs with .json extension are used as-is"""
        data = {
            "name": "test_prop",
            "type": "ref",
            "ref": "test.json"
        }
        prop = RefType(data)
        filename = prop._get_dictionary_filename()
        self.assertEqual(filename, "test.json")

    def test_get_dictionary_filename_without_extension(self):
        """Test that refs without extension get .yaml appended"""
        data = {
            "name": "test_prop",
            "type": "ref",
            "ref": "Circle"
        }
        prop = RefType(data)
        filename = prop._get_dictionary_filename()
        self.assertEqual(filename, "Circle.yaml")

    def test_get_dictionary_filename_with_version(self):
        """Test that refs with version numbers get .yaml appended if missing"""
        data = {
            "name": "test_prop",
            "type": "ref",
            "ref": "observation_persona.1.0.0"
        }
        prop = RefType(data)
        filename = prop._get_dictionary_filename()
        self.assertEqual(filename, "observation_persona.1.0.0.yaml")

    @patch('configurator.services.property.ref_type.Dictionary')
    def test_to_json_schema_appends_yaml_extension(self, mock_dictionary_class):
        """Test that to_json_schema appends .yaml when ref doesn't have extension"""
        # Setup mock
        mock_dictionary = MagicMock()
        mock_dictionary.to_json_schema.return_value = {"type": "object"}
        mock_dictionary_class.return_value = mock_dictionary
        
        # Create RefType with ref without extension
        data = {
            "name": "test_prop",
            "type": "ref",
            "ref": "Circle"
        }
        prop = RefType(data)
        enumerations = Enumerations("test", "0")
        
        # Call to_json_schema
        result = prop.to_json_schema(enumerations)
        
        # Verify Dictionary was called with "Circle.yaml"
        mock_dictionary_class.assert_called_once_with("Circle.yaml")
        self.assertEqual(result, {"type": "object"})

    @patch('configurator.services.property.ref_type.Dictionary')
    def test_to_json_schema_preserves_yaml_extension(self, mock_dictionary_class):
        """Test that to_json_schema preserves .yaml extension when present"""
        # Setup mock
        mock_dictionary = MagicMock()
        mock_dictionary.to_json_schema.return_value = {"type": "object"}
        mock_dictionary_class.return_value = mock_dictionary
        
        # Create RefType with ref with extension
        data = {
            "name": "test_prop",
            "type": "ref",
            "ref": "Circle.yaml"
        }
        prop = RefType(data)
        enumerations = Enumerations("test", "0")
        
        # Call to_json_schema
        result = prop.to_json_schema(enumerations)
        
        # Verify Dictionary was called with "Circle.yaml" (no change)
        mock_dictionary_class.assert_called_once_with("Circle.yaml")
        self.assertEqual(result, {"type": "object"})

    @patch('configurator.services.property.ref_type.Dictionary')
    def test_to_json_schema_error_handling(self, mock_dictionary_class):
        """Test that to_json_schema properly wraps ConfiguratorException"""
        # Setup mock to raise ConfiguratorException
        from configurator.utils.configurator_exception import ConfiguratorEvent
        error_event = ConfiguratorEvent("DIC-01", "GET_DICTIONARY")
        error_event.record_failure("Dictionary not found")
        mock_dictionary_class.side_effect = ConfiguratorException("Dictionary not found", error_event)
        
        # Create RefType
        data = {
            "name": "test_prop",
            "type": "ref",
            "ref": "Missing"
        }
        prop = RefType(data)
        enumerations = Enumerations("test", "0")
        
        # Call to_json_schema and expect ConfiguratorException
        with self.assertRaises(ConfiguratorException) as context:
            prop.to_json_schema(enumerations)
        
        # Verify the exception has meaningful context
        self.assertIn("test_prop", str(context.exception))
        self.assertIn("Missing", str(context.exception))
        # Verify the error event contains sub-events
        self.assertEqual(len(context.exception.event.sub_events), 1)


if __name__ == '__main__':
    unittest.main() 