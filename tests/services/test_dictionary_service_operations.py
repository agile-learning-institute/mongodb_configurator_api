import unittest
from unittest.mock import patch, Mock
from configurator.services.dictionary_services import Dictionary
import os
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.utils.config import Config


class TestDictionary(unittest.TestCase):
    """Focused unit tests for Dictionary class - testing only dictionary service logic"""

    def setUp(self):
        """Set up test environment"""
        self.test_file_name = "test.yaml"
        self.test_document = {
            "file_name": "test.yaml",
            "_locked": False,
            "root": {
                "name": "root",
                "description": "Test dictionary",
                "type": "object",
                "properties": []
            }
        }

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.dictionary_services.Property')
    def test_init_with_file_name(self, mock_property, mock_file_io):
        """Test Dictionary initialization with file name"""
        # Arrange
        mock_file_io.get_document.return_value = self.test_document
        mock_property_instance = Mock()
        mock_property.return_value = mock_property_instance
        
        # Act
        dictionary = Dictionary(self.test_file_name)
        
        # Assert
        self.assertEqual(dictionary.file_name, self.test_file_name)
        self.assertFalse(dictionary._locked)
        mock_file_io.get_document.assert_called_once()
        mock_property.assert_called_once_with(self.test_document.get("root", {}))

    @patch('configurator.services.dictionary_services.Property')
    def test_init_with_document(self, mock_property):
        """Test Dictionary initialization with document"""
        # Arrange
        mock_property_instance = Mock()
        mock_property.return_value = mock_property_instance
        
        # Act
        dictionary = Dictionary(self.test_file_name, self.test_document)
        
        # Assert
        self.assertEqual(dictionary.file_name, self.test_file_name)
        self.assertFalse(dictionary._locked)
        mock_property.assert_called_once_with(self.test_document.get("root", {}))

    def test_init_without_file_name(self):
        """Test Dictionary initialization without file name raises exception"""
        with self.assertRaises(ConfiguratorException) as context:
            Dictionary()
        
        config = Config.get_instance()
        self.assertIn(f"{config.DICTIONARY_FOLDER} file name is required", str(context.exception))

    @patch('configurator.services.dictionary_services.Property')
    def test_to_dict(self, mock_property):
        """Test Dictionary to_dict method"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.to_dict.return_value = {"root": "data"}
        mock_property.return_value = mock_property_instance
        
        dictionary = Dictionary(self.test_file_name, self.test_document)
        
        # Act
        result = dictionary.to_dict()
        
        # Assert
        expected = {
            "file_name": self.test_file_name,
            "_locked": False,
            "root": {"root": "data"}
        }
        self.assertEqual(result, expected)
        mock_property_instance.to_dict.assert_called_once()

    @patch('configurator.services.dictionary_services.Property')
    def test_to_dict_with_locked_dictionary(self, mock_property):
        """Test Dictionary to_dict method with locked dictionary"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.to_dict.return_value = {"test": "root_dict"}
        mock_property.return_value = mock_property_instance
        
        dictionary = Dictionary(self.test_file_name, self.test_document)
        dictionary._locked = True
        
        # Act
        result = dictionary.to_dict()
        
        # Assert
        expected = {
            "file_name": self.test_file_name,
            "_locked": True,
            "root": {"test": "root_dict"}
        }
        self.assertEqual(result, expected)

    @patch('configurator.services.dictionary_services.Property')
    def test_to_json_schema(self, mock_property):
        """Test Dictionary to_json_schema method"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.get_json_schema.return_value = {"type": "object"}
        mock_property.return_value = mock_property_instance
        
        dictionary = Dictionary(self.test_file_name, self.test_document)
        mock_enumerations = Mock()
        
        # Act
        result = dictionary.to_json_schema(mock_enumerations)
        
        # Assert
        self.assertEqual(result, {"type": "object"})
        mock_property_instance.get_json_schema.assert_called_once_with(mock_enumerations, [])

    @patch('configurator.services.dictionary_services.Property')
    def test_to_bson_schema(self, mock_property):
        """Test Dictionary to_bson_schema method"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.get_bson_schema.return_value = {"bsonType": "object"}
        mock_property.return_value = mock_property_instance
        
        dictionary = Dictionary(self.test_file_name, self.test_document)
        mock_enumerations = Mock()
        
        # Act
        result = dictionary.to_bson_schema(mock_enumerations)
        
        # Assert
        self.assertEqual(result, {"bsonType": "object"})
        mock_property_instance.get_bson_schema.assert_called_once_with(mock_enumerations, [])

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.dictionary_services.Property')
    def test_save(self, mock_property, mock_file_io):
        """Test Dictionary save method"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.to_dict.return_value = {"root": "data"}
        mock_property.return_value = mock_property_instance
        mock_file_io.put_document.return_value = {"saved": "document"}
        
        dictionary = Dictionary(self.test_file_name, self.test_document)
        
        # Act
        result = dictionary.save()
        
        # Assert
        self.assertEqual(result, {"saved": "document"})
        mock_file_io.put_document.assert_called_once()

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.dictionary_services.Property')
    def test_delete_unlocked_dictionary(self, mock_property, mock_file_io):
        """Test Dictionary delete method for unlocked dictionary"""
        # Arrange
        mock_property_instance = Mock()
        mock_property.return_value = mock_property_instance
        mock_file_io.delete_document.return_value = Mock()
        
        dictionary = Dictionary(self.test_file_name, self.test_document)
        
        # Act
        result = dictionary.delete()
        
        # Assert
        mock_file_io.delete_document.assert_called_once()


if __name__ == '__main__':
    unittest.main() 