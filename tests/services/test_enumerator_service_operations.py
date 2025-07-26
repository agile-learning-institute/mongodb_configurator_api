import unittest
from unittest.mock import patch, Mock
from configurator.services.enumerators import Enumerators
from configurator.services.enumeration_service import Enumerations
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent


class TestEnumerators(unittest.TestCase):
    """Test cases for Enumerators helper class."""

    @patch('configurator.services.enumerators.FileIO.get_documents')
    def test_init_loads_all_enumerations(self, mock_get_documents):
        """Test Enumerators initialization loads all enumeration files."""
        # Arrange
        mock_files = [Mock(file_name="test1.yaml"), Mock(file_name="test2.yaml")]
        mock_get_documents.return_value = mock_files
        
        with patch('configurator.services.enumerators.Enumerations') as mock_enumerations:
            mock_enum1 = Mock()
            mock_enum2 = Mock()
            mock_enumerations.side_effect = [mock_enum1, mock_enum2]
            
            # Act
            enumerators = Enumerators()
            
            # Assert
            self.assertEqual(len(enumerators.enumerations), 2)
            self.assertEqual(enumerators.enumerations[0], mock_enum1)
            self.assertEqual(enumerators.enumerations[1], mock_enum2)
            mock_enumerations.assert_any_call("test1.yaml")
            mock_enumerations.assert_any_call("test2.yaml")

    @patch('configurator.services.enumerators.FileIO.get_documents')
    def test_get_version_finds_version(self, mock_get_documents):
        """Test get_version finds the correct version."""
        # Arrange
        mock_files = [Mock(file_name="test1.yaml")]
        mock_get_documents.return_value = mock_files
        
        with patch('configurator.services.enumerators.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enum.version = 0
            mock_enumerations.return_value = mock_enum
            
            # Act
            enumerators = Enumerators()
            result = enumerators.get_version("1.0.0.0")
            
            # Assert
            self.assertEqual(result, mock_enum)

    @patch('configurator.services.enumerators.FileIO.get_documents')
    def test_get_version_not_found(self, mock_get_documents):
        """Test get_version when version is not found."""
        # Arrange
        mock_files = [Mock(file_name="test1.yaml")]
        mock_get_documents.return_value = mock_files
        
        with patch('configurator.services.enumerators.Enumerations') as mock_enumerations:
            mock_enum = Mock()
            mock_enum.version = 1  # Different from the requested version (0)
            mock_enumerations.return_value = mock_enum
            
            # Act & Assert
            enumerators = Enumerators()
            with self.assertRaises(ConfiguratorException):
                enumerators.get_version("999.0.0.0")

    @patch('configurator.services.enumerators.FileIO.get_documents')
    def test_init_with_file_io_exception(self, mock_get_documents):
        """Test Enumerators initialization when FileIO raises exception."""
        # Arrange
        event = ConfiguratorEvent("ENU-01", "INIT")
        mock_get_documents.side_effect = ConfiguratorException("File not found", event)
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException):
            Enumerators()


class TestEnumerations(unittest.TestCase):
    """Test cases for Enumerations service class."""

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_init(self, mock_get_document):
        """Test Enumerations initialization"""
        # Arrange
        test_data = {
            "version": 0,
            "enumerators": [{"name": "test_enum", "values": [{"value": "value1", "description": "desc1"}]}]
        }
        mock_get_document.return_value = test_data
        
        # Act
        enum = Enumerations("test.yaml")
        
        # Assert
        self.assertEqual(enum.file_name, "test.yaml")
        self.assertEqual(len(enum.enumerators), 1)
        self.assertEqual(enum.enumerators[0]["name"], "test_enum")

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_init_defaults(self, mock_get_document):
        """Test Enumerations initialization with defaults"""
        # Arrange
        test_data = {}
        mock_get_document.return_value = test_data
        
        # Act
        enum = Enumerations("test.yaml")
        
        # Assert
        self.assertEqual(enum.file_name, "test.yaml")
        self.assertEqual(enum.version, 0)
        self.assertEqual(enum.enumerators, [])

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_to_dict(self, mock_get_document):
        """Test Enumerations to_dict method"""
        # Arrange
        test_data = {
            "version": 0,
            "enumerators": [
                {"name": "test_enum", "values": [{"value": "value1", "description": "First value"}]}
            ]
        }
        mock_get_document.return_value = test_data
        
        # Act
        enum = Enumerations("test.yaml")
        result = enum.to_dict()
        
        # Assert
        expected = {
            "file_name": "test.yaml",
            "_locked": False,
            "version": 0,
            "enumerators": [
                {"name": "test_enum", "values": [{"value": "value1", "description": "First value"}]}
            ]
        }
        self.assertEqual(result, expected)

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_get_enum_values(self, mock_get_document):
        """Test Enumerations get_enum_values method"""
        # Arrange
        test_data = {
            "version": 0,
            "enumerators": [
                {"name": "test_enum", "values": [{"value": "value1", "description": "desc1"}, {"value": "value2", "description": "desc2"}]}
            ]
        }
        mock_get_document.return_value = test_data
        
        # Act
        enum = Enumerations("test.yaml")
        result = enum.get_enum_values("test_enum")
        
        # Assert
        expected = {"value1", "value2"}
        self.assertEqual(set(result), expected)


if __name__ == '__main__':
    unittest.main() 