import unittest
from unittest.mock import Mock, patch
from configurator.services.configuration_services import Configuration
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.utils.config import Config


class TestConfiguration(unittest.TestCase):
    
    def setUp(self):
        self.test_file_name = "test.yaml"
        self.test_document = {
            "title": "Test Configuration",
            "description": "Test configuration description",
            "versions": [
                {"version": "1.0.0", "collection_version": "1.0.0"},
                {"version": "1.1.0", "collection_version": "1.1.0"}
            ],
            "_locked": False
        }

    @patch('configurator.services.service_base.FileIO')
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
            Configuration()
        
        config = Config.get_instance()
        self.assertIn(f"{config.CONFIGURATION_FOLDER} file name is required", str(context.exception))

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

    @patch('configurator.services.service_base.FileIO')
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

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.configuration_services.Version')
    def test_delete_unlocked_configuration(self, mock_version, mock_file_io):
        """Test Configuration delete method for unlocked configuration"""
        # Arrange
        mock_version_instances = [Mock(), Mock()]
        mock_version.side_effect = mock_version_instances
        mock_file_io.delete_document.return_value = Mock()
        
        config = Configuration(self.test_file_name, self.test_document)
        
        # Act
        result = config.delete()
        
        # Assert
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

    def test_get_json_schema(self):
        """Test Configuration get_json_schema method"""
        # Arrange
        with patch('configurator.services.configuration_services.Enumerators') as mock_enumerators:
            mock_enumerators_instance = Mock()
            mock_enumerators.return_value = mock_enumerators_instance
            mock_enumerators_instance.getVersion.return_value = Mock()
            
            with patch('configurator.services.configuration_version.Dictionary') as mock_dictionary:
                mock_dictionary_instance = Mock()
                mock_dictionary_instance.get_json_schema.return_value = {"schema": "json"}
                mock_dictionary.return_value = mock_dictionary_instance
                
                config = Configuration(self.test_file_name, self.test_document)
                
                # Act
                result = config.get_json_schema("1.0.0.0")
                
                # Assert
                self.assertEqual(result, {"schema": "json"})

    def test_get_bson_schema(self):
        """Test Configuration get_bson_schema method"""
        # Arrange
        with patch('configurator.services.configuration_services.Enumerators') as mock_enumerators:
            mock_enumerators_instance = Mock()
            mock_enumerators.return_value = mock_enumerators_instance
            mock_enumerators_instance.getVersion.return_value = Mock()
            
            with patch('configurator.services.configuration_version.Dictionary') as mock_dictionary:
                mock_dictionary_instance = Mock()
                mock_dictionary_instance.get_bson_schema.return_value = {"schema": "bson"}
                mock_dictionary.return_value = mock_dictionary_instance
                
                config = Configuration(self.test_file_name, self.test_document)
                
                # Act
                result = config.get_bson_schema("1.0.0.0")
                
                # Assert
                self.assertEqual(result, {"schema": "bson"})


class TestVersion(unittest.TestCase):
    
    def setUp(self):
        self.test_version_data = {
            "version": "1.0.0",
            "collection_version": "1.0.0",
            "_locked": False
        }
    
    def test_version_init(self):
        """Test Version initialization"""
        # Act
        from configurator.services.configuration_version import Version
        version = Version("test_collection", self.test_version_data)
        
        # Assert
        self.assertEqual(version.version_str, "1.0.0.0")
        self.assertEqual(version.collection_name, "test_collection")
        self.assertFalse(version._locked)
    
    def test_version_to_dict(self):
        """Test Version to_dict method"""
        # Arrange
        from configurator.services.configuration_version import Version
        version = Version("test_collection", self.test_version_data)
        
        # Act
        result = version.to_dict()
        
        # Assert
        expected = {
            "version": "1.0.0.0",
            "drop_indexes": [],
            "add_indexes": [],
            "migrations": [],
            "test_data": None,
            "_locked": False
        }
        self.assertEqual(result, expected)
    
    def test_version_init_defaults(self):
        """Test Version initialization with defaults"""
        # Arrange
        version_data = {"version": "1.0.0"}
        
        # Act
        from configurator.services.configuration_version import Version
        version = Version("test_collection", version_data)
        
        # Assert
        self.assertEqual(version.version_str, "1.0.0.0")
        self.assertEqual(version.collection_name, "test_collection")
        self.assertFalse(version._locked) 