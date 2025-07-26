import unittest
from unittest.mock import patch, MagicMock, Mock
from configurator.services.template_service import TemplateService
import os
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent


class TestTemplateService(unittest.TestCase):
    """Focused unit tests for TemplateService class"""

    def setUp(self):
        """Set up test environment"""
        self.test_collection_name = "test_collection"
        self.test_configuration_file = "test_collection.yaml"
        self.test_dictionary_file = "test_collection.0.0.1.yaml"

    @patch('configurator.services.template_service.Configuration')
    @patch('configurator.services.template_service.Dictionary')
    @patch('configurator.services.template_service.FileIO')
    def test_new_configuration(self, mock_file_io, mock_dictionary, mock_configuration):
        """Test TemplateService.new_configuration method"""
        # Arrange
        mock_config_instance = Mock()
        mock_configuration.return_value = mock_config_instance
        
        # Act
        result = TemplateService.new_configuration(self.test_collection_name, self.test_configuration_file)
        
        # Assert
        self.assertEqual(result, mock_config_instance)
        mock_configuration.assert_called_once_with(
            file_name=self.test_configuration_file,
            document={
                "file_name": self.test_configuration_file,
                "title": f"{self.test_collection_name} Configuration",
                "description": f"Collection for managing {self.test_collection_name}",
                "versions": [{"version": "0.0.1.0"}]
            }
        )

    @patch('configurator.services.template_service.Configuration')
    @patch('configurator.services.template_service.Dictionary')
    @patch('configurator.services.template_service.FileIO')
    def test_new_dictionary(self, mock_file_io, mock_dictionary, mock_configuration):
        """Test TemplateService.new_dictionary method"""
        # Arrange
        mock_dict_instance = Mock()
        mock_dictionary.return_value = mock_dict_instance
        
        # Act
        result = TemplateService.new_dictionary(self.test_collection_name, self.test_dictionary_file)
        
        # Assert
        self.assertEqual(result, mock_dict_instance)
        mock_dictionary.assert_called_once_with(
            file_name=self.test_dictionary_file,
            document={
                "file_name": self.test_dictionary_file,
                "root": {
                    "description": f"A {self.test_collection_name} collection for testing the schema system",
                    "type": "object",
                    "properties": [
                        {
                            "name": "_id",
                            "description": "A unique identifier",
                            "type": "identifier",
                            "required": True
                        },
                        {
                            "name": "name",
                            "description": "The name",
                            "type": "word",
                            "required": True
                        },
                        {
                            "name": "status",
                            "description": "The current status",
                            "type": "enum",
                            "enums": "default_status",
                            "required": True
                        },
                        {
                            "name": "last_saved",
                            "description": "The last time this document was saved",
                            "type": "breadcrumb",
                            "required": True
                        }
                    ]
                }
            }
        )

    def test_new_configuration_without_file_name(self):
        """Test TemplateService.new_configuration method without file name"""
        # Note: The source code has a defect - it passes None as file_name to Configuration
        # which raises an exception. This test documents that defect.
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            TemplateService.new_configuration(self.test_collection_name)
        
        self.assertIn("Configuration file name is required", str(context.exception))

    def test_new_dictionary_without_file_name(self):
        """Test TemplateService.new_dictionary method without file name"""
        # Note: The source code has a defect - it passes None as file_name to Dictionary
        # which raises an exception. This test documents that defect.
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            TemplateService.new_dictionary(self.test_collection_name)
        
        self.assertIn("Dictionary file name is required", str(context.exception))

    def test_create_collection_defects(self):
        """Test TemplateService.create_collection method defects"""
        # Note: The source code has several defects:
        # 1. It's a static method but uses 'self' parameter
        # 2. It references 'self.config', 'self.file_name', 'self.dictionary_file_name' 
        #    which don't exist in a static method
        # 3. It doesn't handle None file names properly
        # 4. Version constructor is called with 4 arguments but only expects 3
        
        # Act & Assert
        with self.assertRaises((AttributeError, TypeError)) as context:
            TemplateService.create_collection(None, self.test_collection_name)
        
        # Should fail due to either:
        # - 'NoneType' object has no attribute 'config' (AttributeError)
        # - Version.__init__() takes 3 positional arguments but 4 were given (TypeError)
        exception_str = str(context.exception)
        self.assertTrue(
            "'NoneType' object has no attribute 'config'" in exception_str or
            "Version.__init__() takes 3 positional arguments but 4 were given" in exception_str
        )


if __name__ == '__main__':
    unittest.main() 