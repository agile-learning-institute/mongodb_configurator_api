import unittest
from unittest.mock import patch, MagicMock, Mock
from configurator.services.type_services import Type
import os
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent


class TestType(unittest.TestCase):
    """Focused unit tests for Type class - testing only type service logic"""

    def setUp(self):
        """Set up test environment"""
        self.test_file_name = "test.yaml"
        self.test_document = {
            "file_name": "test.yaml",
            "_locked": False,
            "root": {
                "name": "root",
                "description": "Test type",
                "type": "object",
                "properties": []
            }
        }

    @patch('configurator.services.type_services.FileIO')
    @patch('configurator.services.type_services.Property')
    def test_init_with_file_name(self, mock_property, mock_file_io):
        """Test Type initialization with file name"""
        # Arrange
        mock_file_io.get_document.return_value = self.test_document
        mock_property_instance = Mock()
        mock_property.return_value = mock_property_instance
        
        # Act
        type_obj = Type(self.test_file_name)
        
        # Assert
        self.assertEqual(type_obj.file_name, self.test_file_name)
        self.assertFalse(type_obj._locked)
        self.assertEqual(type_obj.root, mock_property_instance)
        mock_file_io.get_document.assert_called_once()
        mock_property.assert_called_once_with(self.test_document["root"])

    @patch('configurator.services.type_services.Property')
    def test_init_with_document(self, mock_property):
        """Test Type initialization with document"""
        # Arrange
        mock_property_instance = Mock()
        mock_property.return_value = mock_property_instance
        
        # Act
        type_obj = Type(self.test_file_name, self.test_document)
        
        # Assert
        self.assertEqual(type_obj.file_name, self.test_file_name)
        self.assertFalse(type_obj._locked)
        self.assertEqual(type_obj.root, mock_property_instance)
        mock_property.assert_called_once_with(self.test_document["root"])

    def test_init_without_file_name(self):
        """Test Type initialization without file name raises exception"""
        with self.assertRaises(ConfiguratorException) as context:
            Type(None, self.test_document)
        
        self.assertIn("Type file name is required", str(context.exception))

    @patch('configurator.services.type_services.Property')
    def test_to_dict(self, mock_property):
        """Test Type to_dict method"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.to_dict.return_value = {"test": "root_dict"}
        mock_property.return_value = mock_property_instance
        
        type_obj = Type(self.test_file_name, self.test_document)
        
        # Act
        result = type_obj.to_dict()
        
        # Assert
        expected = {
            "file_name": self.test_file_name,
            "_locked": False,
            "root": {"test": "root_dict"}
        }
        self.assertEqual(result, expected)
        mock_property_instance.to_dict.assert_called_once()

    @patch('configurator.services.type_services.Property')
    def test_to_dict_with_locked_type(self, mock_property):
        """Test Type to_dict method with locked type"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.to_dict.return_value = {"test": "root_dict"}
        mock_property.return_value = mock_property_instance
        
        type_obj = Type(self.test_file_name, self.test_document)
        type_obj._locked = True
        
        # Act
        result = type_obj.to_dict()
        
        # Assert
        expected = {
            "file_name": self.test_file_name,
            "_locked": True,
            "root": {"test": "root_dict"}
        }
        self.assertEqual(result, expected)

    @patch('configurator.services.type_services.Property')
    def test_to_json_schema(self, mock_property):
        """Test Type to_json_schema method"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.to_json_schema.return_value = {"type": "object"}
        mock_property.return_value = mock_property_instance
        
        type_obj = Type(self.test_file_name, self.test_document)
        mock_enumerations = Mock()
        
        # Act
        result = type_obj.to_json_schema(mock_enumerations)
        
        # Assert
        self.assertEqual(result, {"type": "object"})
        mock_property_instance.to_json_schema.assert_called_once_with(mock_enumerations, [])

    @patch('configurator.services.type_services.Property')
    def test_to_bson_schema(self, mock_property):
        """Test Type to_bson_schema method"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.to_bson_schema.return_value = {"bsonType": "object"}
        mock_property.return_value = mock_property_instance
        
        type_obj = Type(self.test_file_name, self.test_document)
        mock_enumerations = Mock()
        
        # Act
        result = type_obj.to_bson_schema(mock_enumerations)
        
        # Assert
        self.assertEqual(result, {"bsonType": "object"})
        mock_property_instance.to_bson_schema.assert_called_once_with(mock_enumerations, [])

    @patch('configurator.services.type_services.FileIO')
    @patch('configurator.services.type_services.Property')
    def test_save(self, mock_property, mock_file_io):
        """Test Type save method"""
        # Arrange
        mock_property_instance = Mock()
        mock_property_instance.to_dict.return_value = {"test": "root_dict"}
        mock_property.return_value = mock_property_instance
        mock_file_io.put_document.return_value = {"saved": "document"}
        
        type_obj = Type(self.test_file_name, self.test_document)
        
        # Act
        result = type_obj.save()
        
        # Assert
        self.assertEqual(result, {"saved": "document"})
        mock_file_io.put_document.assert_called_once()

    @patch('configurator.services.type_services.FileIO')
    @patch('configurator.services.type_services.Property')
    @patch('configurator.services.type_services.Type')
    def test_delete_unlocked_type(self, mock_type_class, mock_property, mock_file_io):
        """Test Type delete method for unlocked type"""
        # Arrange
        mock_property_instance = Mock()
        mock_property.return_value = mock_property_instance
        mock_file_io.delete_document.return_value = True
        
        type_obj = Type(self.test_file_name, self.test_document)
        type_obj._locked = False
        
        # Act
        result = type_obj.delete()
        
        # Assert
        self.assertTrue(result)
        mock_file_io.delete_document.assert_called_once()

    @patch('configurator.services.type_services.Property')
    def test_delete_locked_type(self, mock_property):
        """Test Type delete method for locked type raises exception"""
        # Arrange
        mock_property_instance = Mock()
        mock_property.return_value = mock_property_instance
        
        type_obj = Type(self.test_file_name, self.test_document)
        type_obj._locked = True
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            type_obj.delete()
        
        self.assertIn("Cannot delete locked type", str(context.exception))

    @patch('configurator.services.type_services.FileIO')
    @patch('configurator.services.type_services.Type')
    def test_lock_all_types_success(self, mock_type_class, mock_file_io):
        """Test Type.lock_all method success"""
        # Arrange
        mock_files = [Mock(file_name="type1.yaml"), Mock(file_name="type2.yaml")]
        mock_file_io.get_documents.return_value = mock_files
        
        mock_type1 = Mock()
        mock_type2 = Mock()
        mock_type_class.side_effect = [mock_type1, mock_type2]
        
        # Act
        result = Type.lock_all(True)
        
        # Assert
        self.assertIsInstance(result, ConfiguratorEvent)
        self.assertEqual(mock_type_class.call_count, 2)
        self.assertEqual(mock_type1._locked, True)
        self.assertEqual(mock_type2._locked, True)
        mock_type1.save.assert_called_once()
        mock_type2.save.assert_called_once()

    @patch('configurator.services.type_services.FileIO')
    @patch('configurator.services.type_services.Type')
    def test_lock_all_types_failure(self, mock_type_class, mock_file_io):
        """Test Type.lock_all method failure"""
        # Arrange
        mock_files = [Mock(file_name="type1.yaml")]
        mock_file_io.get_documents.return_value = mock_files
        
        test_event = ConfiguratorEvent(event_id="TEST-01", event_type="TEST_ERROR")
        mock_type_class.side_effect = ConfiguratorException("Test error", test_event)
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            Type.lock_all(True)
        
        self.assertIn("Cannot lock all types", str(context.exception))


if __name__ == '__main__':
    unittest.main() 