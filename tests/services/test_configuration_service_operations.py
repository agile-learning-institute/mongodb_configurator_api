import unittest
from unittest.mock import patch, MagicMock, Mock
from configurator.services.configuration_services import Configuration
from configurator.services.configuration_version import Version
import os
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent


class TestConfiguration(unittest.TestCase):
    """Focused unit tests for Configuration class"""

    def setUp(self):
        """Set up test environment"""
        self.test_file_name = "test.yaml"
        self.test_document = {
            "file_name": "test.yaml",
            "_locked": False,
            "title": "Test Configuration",
            "description": "Test configuration description",
            "versions": [
                {
                    "version": "1.0.0",
                    "drop_indexes": ["old_index"],
                    "add_indexes": [{"name": "new_index", "keys": [{"field": "name", "direction": 1}]}],
                    "migrations": ["migration1.json"],
                    "test_data": "test_data.json",
                    "_locked": False
                },
                {
                    "version": "1.1.0",
                    "drop_indexes": [],
                    "add_indexes": [],
                    "migrations": [],
                    "test_data": None,
                    "_locked": False
                }
            ]
        }

    @patch('configurator.services.configuration_services.FileIO')
    @patch('configurator.services.configuration_services.Version')
    def test_init_with_file_name(self, mock_version, mock_file_io):
        """Test Configuration initialization with file name"""
        # Arrange
        mock_file_io.get_document.return_value = self.test_document
        mock_version_instances = [Mock(), Mock()]
        mock_version.side_effect = mock_version_instances
        
        # Act
        config = Configuration(self.test_file_name)
        
        # Assert
        self.assertEqual(config.file_name, self.test_file_name)
        self.assertFalse(config._locked)
        self.assertEqual(config.title, "Test Configuration")
        self.assertEqual(config.description, "Test configuration description")
        self.assertEqual(len(config.versions), 2)
        self.assertEqual(mock_version.call_count, 2)
        mock_file_io.get_document.assert_called_once()

    @patch('configurator.services.configuration_services.Version')
    def test_init_with_document(self, mock_version):
        """Test Configuration initialization with document"""
        # Arrange
        mock_version_instances = [Mock(), Mock()]
        mock_version.side_effect = mock_version_instances
        
        # Act
        config = Configuration(self.test_file_name, self.test_document)
        
        # Assert
        self.assertEqual(config.file_name, self.test_file_name)
        self.assertFalse(config._locked)
        self.assertEqual(config.title, "Test Configuration")
        self.assertEqual(config.description, "Test configuration description")
        self.assertEqual(len(config.versions), 2)
        self.assertEqual(mock_version.call_count, 2)

    def test_init_without_file_name(self):
        """Test Configuration initialization without file name raises exception"""
        with self.assertRaises(ConfiguratorException) as context:
            Configuration(None, self.test_document)
        
        self.assertIn("Configuration file name is required", str(context.exception))

    @patch('configurator.services.configuration_services.Version')
    def test_to_dict(self, mock_version):
        """Test Configuration to_dict method"""
        # Arrange
        mock_version1 = Mock()
        mock_version1.to_dict.return_value = {"version": "1.0.0"}
        mock_version2 = Mock()
        mock_version2.to_dict.return_value = {"version": "1.1.0"}
        mock_version.side_effect = [mock_version1, mock_version2]
        
        config = Configuration(self.test_file_name, self.test_document)
        
        # Act
        result = config.to_dict()
        
        # Assert
        expected = {
            "file_name": self.test_file_name,
            "_locked": False,
            "title": "Test Configuration",
            "description": "Test configuration description",
            "versions": [
                {"version": "1.0.0"},
                {"version": "1.1.0"}
            ]
        }
        self.assertEqual(result, expected)
        mock_version1.to_dict.assert_called_once()
        mock_version2.to_dict.assert_called_once()

    @patch('configurator.services.configuration_services.FileIO')
    @patch('configurator.services.configuration_services.Version')
    def test_save(self, mock_version, mock_file_io):
        """Test Configuration save method"""
        # Arrange
        mock_version_instances = [Mock(), Mock()]
        mock_version.side_effect = mock_version_instances
        mock_file_io.put_document.return_value = {"saved": "document"}
        
        config = Configuration(self.test_file_name, self.test_document)
        
        # Act
        result = config.save()
        
        # Assert
        self.assertEqual(result, {"saved": "document"})
        mock_file_io.put_document.assert_called_once()

    @patch('configurator.services.configuration_services.FileIO')
    @patch('configurator.services.configuration_services.Version')
    def test_delete_unlocked_configuration(self, mock_version, mock_file_io):
        """Test Configuration delete method for unlocked configuration"""
        # Arrange
        mock_version_instances = [Mock(), Mock()]
        mock_version.side_effect = mock_version_instances
        mock_file_io.delete_document.return_value = True
        
        config = Configuration(self.test_file_name, self.test_document)
        config._locked = False
        
        # Act
        result = config.delete()
        
        # Assert
        self.assertTrue(result)
        mock_file_io.delete_document.assert_called_once()

    @patch('configurator.services.configuration_services.Version')
    def test_delete_locked_configuration(self, mock_version):
        """Test Configuration delete method for locked configuration raises exception"""
        # Arrange
        mock_version_instances = [Mock(), Mock()]
        mock_version.side_effect = mock_version_instances
        
        config = Configuration(self.test_file_name, self.test_document)
        config._locked = True
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            config.delete()
        
        self.assertIn("Cannot delete locked configuration", str(context.exception))

    @patch('configurator.services.configuration_services.FileIO')
    @patch('configurator.services.configuration_services.Configuration')
    def test_lock_all_configurations_success(self, mock_configuration_class, mock_file_io):
        """Test Configuration.lock_all method success"""
        # Arrange
        mock_files = [Mock(file_name="config1.yaml"), Mock(file_name="config2.yaml")]
        mock_file_io.get_documents.return_value = mock_files
        
        mock_config1 = Mock()
        mock_config2 = Mock()
        mock_configuration_class.side_effect = [mock_config1, mock_config2]
        
        # Act
        result = Configuration.lock_all(True)
        
        # Assert
        self.assertIsInstance(result, ConfiguratorEvent)
        self.assertEqual(mock_configuration_class.call_count, 2)
        self.assertEqual(mock_config1._locked, True)
        self.assertEqual(mock_config2._locked, True)
        mock_config1.save.assert_called_once()
        mock_config2.save.assert_called_once()

    @patch('configurator.services.configuration_services.FileIO')
    @patch('configurator.services.configuration_services.Configuration')
    def test_lock_all_configurations_failure(self, mock_configuration_class, mock_file_io):
        """Test Configuration.lock_all method failure"""
        # Arrange
        mock_files = [Mock(file_name="config1.yaml")]
        mock_file_io.get_documents.return_value = mock_files
        
        test_event = ConfiguratorEvent(event_id="TEST-01", event_type="TEST_ERROR")
        mock_configuration_class.side_effect = ConfiguratorException("Test error", test_event)
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            Configuration.lock_all(True)
        
        self.assertIn("Cannot lock all configurations", str(context.exception))


class TestVersion(unittest.TestCase):
    """Focused unit tests for Version class"""

    def setUp(self):
        """Set up test environment"""
        self.test_collection_name = "test_collection"
        self.test_document = {
            "version": "1.0.0",
            "drop_indexes": ["old_index"],
            "add_indexes": [{"name": "new_index", "keys": [{"field": "name", "direction": 1}]}],
            "migrations": ["migration1.json"],
            "test_data": "test_data.json",
            "_locked": False
        }

    @patch('configurator.services.configuration_version.VersionNumber')
    def test_version_init(self, mock_version_number):
        """Test Version initialization"""
        # Arrange
        mock_version_number_instance = Mock()
        mock_version_number_instance.get_version_str.return_value = "1.0.0"
        mock_version_number.return_value = mock_version_number_instance
        
        # Act
        version = Version(self.test_collection_name, self.test_document)
        
        # Assert
        self.assertEqual(version.collection_name, self.test_collection_name)
        self.assertEqual(version.version_str, "1.0.0")
        self.assertEqual(version.drop_indexes, ["old_index"])
        self.assertEqual(version.add_indexes, [{"name": "new_index", "keys": [{"field": "name", "direction": 1}]}])
        self.assertEqual(version.migrations, ["migration1.json"])
        self.assertEqual(version.test_data, "test_data.json")
        self.assertFalse(version._locked)
        mock_version_number.assert_called_once_with("test_collection.1.0.0")

    @patch('configurator.services.configuration_version.VersionNumber')
    def test_version_to_dict(self, mock_version_number):
        """Test Version to_dict method"""
        # Arrange
        mock_version_number_instance = Mock()
        mock_version_number_instance.get_version_str.return_value = "1.0.0"
        mock_version_number.return_value = mock_version_number_instance
        
        version = Version(self.test_collection_name, self.test_document)
        
        # Act
        result = version.to_dict()
        
        # Assert
        expected = {
            "version": "1.0.0",
            "drop_indexes": ["old_index"],
            "add_indexes": [{"name": "new_index", "keys": [{"field": "name", "direction": 1}]}],
            "migrations": ["migration1.json"],
            "test_data": "test_data.json",
            "_locked": False
        }
        self.assertEqual(result, expected)

    @patch('configurator.services.configuration_version.VersionNumber')
    def test_version_init_defaults(self, mock_version_number):
        """Test Version initialization with defaults"""
        # Arrange
        mock_version_number_instance = Mock()
        mock_version_number_instance.get_version_str.return_value = "1.0.0"
        mock_version_number.return_value = mock_version_number_instance
        
        document = {"version": "1.0.0"}
        
        # Act
        version = Version(self.test_collection_name, document)
        
        # Assert
        self.assertEqual(version.drop_indexes, [])
        self.assertEqual(version.add_indexes, [])
        self.assertEqual(version.migrations, [])
        self.assertIsNone(version.test_data)
        self.assertFalse(version._locked)


if __name__ == '__main__':
    unittest.main() 