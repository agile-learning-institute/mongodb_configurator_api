import unittest
from unittest.mock import patch, MagicMock, Mock
from configurator.services.enumerator_service import Enumerators
from configurator.services.enumerations import Enumerations
import os
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent


class TestEnumerations(unittest.TestCase):
    """Focused unit tests for Enumerations class"""

    def setUp(self):
        """Set up test environment"""
        self.test_enumeration = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "First value"},
                {"value": "value2", "description": "Second value"},
                {"value": "value3", "description": "Third value"}
            ],
            "_locked": False
        }

    def test_enumerations_init(self):
        """Test Enumerations initialization"""
        enum = Enumerations(self.test_enumeration)
        self.assertEqual(enum.name, "test_enum")
        self.assertEqual(len(enum.values), 3)
        self.assertFalse(enum._locked)
        self.assertEqual(enum.values[0]["value"], "value1")
        self.assertEqual(enum.values[0]["description"], "First value")

    def test_enumerations_init_defaults(self):
        """Test Enumerations initialization with defaults"""
        enum = Enumerations({})
        self.assertIsNone(enum.name)
        self.assertEqual(len(enum.values), 0)
        self.assertFalse(enum._locked)

    def test_enumerations_to_dict(self):
        """Test Enumerations to_dict method"""
        enum = Enumerations(self.test_enumeration)
        result = enum.to_dict()
        expected = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "First value"},
                {"value": "value2", "description": "Second value"},
                {"value": "value3", "description": "Third value"}
            ]
        }
        self.assertEqual(result, expected)

    def test_enumerations_get_enum_dict(self):
        """Test Enumerations get_enum_dict method"""
        enum = Enumerations(self.test_enumeration)
        result = enum.get_enum_dict()
        expected = {
            "value1": "First value",
            "value2": "Second value", 
            "value3": "Third value"
        }
        self.assertEqual(result, expected)

    def test_enumerations_get_enum_values(self):
        """Test Enumerations get_enum_values method"""
        enum = Enumerations(self.test_enumeration)
        result = enum.get_enum_values("test_enum")
        expected = {"value1", "value2", "value3"}
        self.assertEqual(set(result), expected)


class TestEnumerators(unittest.TestCase):
    """Focused unit tests for Enumerators class"""

    def setUp(self):
        """Set up test environment"""
        self.test_file_name = "test.yaml"
        self.test_document = {
            "file_name": "test.yaml",
            "_locked": False,
            "version": 1,
            "enumerators": [
                {
                    "name": "enum1",
                    "values": [
                        {"value": "value1", "description": "First value"},
                        {"value": "value2", "description": "Second value"}
                    ]
                },
                {
                    "name": "enum2", 
                    "values": [
                        {"value": "value3", "description": "Third value"},
                        {"value": "value4", "description": "Fourth value"}
                    ]
                }
            ]
        }

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.enumerator_service.Enumerations')
    def test_init_with_file_name(self, mock_enumerations, mock_file_io):
        """Test Enumerators initialization with file name"""
        # Arrange
        mock_file_io.get_document.return_value = self.test_document
        mock_enumeration_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enumeration_instances
        
        # Act
        enumerators = Enumerators(self.test_file_name)
        
        # Assert
        self.assertEqual(enumerators.file_name, self.test_file_name)
        self.assertFalse(enumerators._locked)
        self.assertEqual(enumerators.version, 1)
        self.assertEqual(len(enumerators.enumerations), 2)
        mock_file_io.get_document.assert_called_once()
        self.assertEqual(mock_enumerations.call_count, 2)

    @patch('configurator.services.enumerator_service.Enumerations')
    def test_init_with_document(self, mock_enumerations):
        """Test Enumerators initialization with document"""
        # Arrange
        mock_enumeration_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enumeration_instances
        
        # Act
        enumerators = Enumerators(self.test_file_name, self.test_document)
        
        # Assert
        self.assertEqual(enumerators.file_name, self.test_file_name)
        self.assertFalse(enumerators._locked)
        self.assertEqual(enumerators.version, 1)
        self.assertEqual(len(enumerators.enumerations), 2)
        self.assertEqual(mock_enumerations.call_count, 2)

    def test_init_without_file_name(self):
        """Test Enumerators initialization without file name raises exception"""
        with self.assertRaises(ConfiguratorException) as context:
            Enumerators(None, self.test_document)
        
        self.assertIn("enumerator file name is required", str(context.exception))

    @patch('configurator.services.enumerator_service.Enumerations')
    def test_to_dict(self, mock_enumerations):
        """Test Enumerators to_dict method"""
        # Arrange
        mock_enumeration1 = Mock()
        mock_enumeration1.to_dict.return_value = {"enum1": "data"}
        mock_enumeration2 = Mock()
        mock_enumeration2.to_dict.return_value = {"enum2": "data"}
        mock_enumerations.side_effect = [mock_enumeration1, mock_enumeration2]
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        
        # Act
        result = enumerators.to_dict()
        
        # Assert
        expected = {
            "file_name": self.test_file_name,
            "_locked": False,
            "enumerations": [
                {"enum1": "data"},
                {"enum2": "data"}
            ]
        }
        self.assertEqual(result, expected)
        mock_enumeration1.to_dict.assert_called_once()
        mock_enumeration2.to_dict.assert_called_once()

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.enumerator_service.Enumerators')
    def test_save(self, mock_enumerations, mock_file_io):
        """Test Enumerators save method"""
        # Arrange
        mock_enumeration_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enumeration_instances
        mock_file_io.put_document.return_value = {"saved": "document"}
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        
        # Act
        result = enumerators.save()
        
        # Assert
        self.assertEqual(result, {"saved": "document"})
        mock_file_io.put_document.assert_called_once()

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.enumerator_service.Enumerators')
    def test_delete_unlocked_enumerators(self, mock_enumerations, mock_file_io):
        """Test Enumerators delete method for unlocked enumerators"""
        # Arrange
        mock_enumeration_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enumeration_instances
        mock_file_io.delete_document.return_value = Mock()
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        
        # Act
        result = enumerators.delete()
        
        # Assert
        mock_file_io.delete_document.assert_called_once()

    @patch('configurator.services.enumerator_service.Enumerations')
    def test_delete_locked_enumerators(self, mock_enumerations):
        """Test Enumerators delete method for locked enumerators raises exception"""
        # Arrange
        mock_enumeration_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enumeration_instances
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        enumerators._locked = True
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            enumerators.delete()
        
        self.assertIn("Cannot delete locked enumerator", str(context.exception))

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.service_base.Config')
    def test_lock_all_enumerators_success(self, mock_config, mock_file_io):
        """Test Enumerators lock_all method success"""
        # Arrange
        mock_config_instance = Mock()
        mock_config_instance.ENUMERATOR_FOLDER = "enumerators"
        mock_config.get_instance.return_value = mock_config_instance
        
        mock_file1 = Mock()
        mock_file1.file_name = "enum1.yaml"
        mock_file2 = Mock()
        mock_file2.file_name = "enum2.yaml"
        mock_files = [mock_file1, mock_file2]
        mock_file_io.get_documents.return_value = mock_files
        
        # Mock the Enumerators constructor to return instances
        with patch('configurator.services.enumerator_service.Enumerators') as mock_enum_class:
            mock_enum1 = Mock()
            mock_enum2 = Mock()
            mock_enum_class.side_effect = [mock_enum1, mock_enum2]
            
            # Act
            result = Enumerators.lock_all()
            
            # Assert
            self.assertEqual(mock_enum_class.call_count, 2)
            mock_enum1._locked = True
            mock_enum2._locked = True
            mock_enum1.save.assert_called_once()
            mock_enum2.save.assert_called_once()

    @patch('configurator.services.service_base.FileIO')
    def test_lock_all_enumerators_failure(self, mock_file_io):
        """Test Enumerators lock_all method failure"""
        # Arrange
        mock_file1 = Mock()
        mock_file1.file_name = "enum1.yaml"
        mock_files = [mock_file1]
        mock_file_io.get_documents.return_value = mock_files
        
        # Mock FileIO.get_document to raise an exception when Enumerators constructor tries to load the document
        mock_file_io.get_document.side_effect = Exception("Test error")
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            Enumerators.lock_all()
        
        self.assertIn("Cannot lock all enumerators", str(context.exception))


if __name__ == '__main__':
    unittest.main() 