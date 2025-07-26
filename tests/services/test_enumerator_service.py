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
            mock_enum.version_str = "1.0.0"
            mock_enumerations.return_value = mock_enum
            
            # Act
            enumerators = Enumerators()
            result = enumerators.get_version("1.0.0")
            
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
            mock_enum.version_str = "1.0.0"
            mock_enumerations.return_value = mock_enum
            
            # Act & Assert
            enumerators = Enumerators()
            with self.assertRaises(ConfiguratorException):
                enumerators.get_version("999.0.0")


class TestEnumerations(unittest.TestCase):
    """Test cases for Enumerations service class."""

    def test_init_with_none_data_loads_file(self):
        """Test Enumerations initialization loads from file."""
        # Arrange
        test_data = {
            "name": "test_enum",
            "values": [{"value": "value1", "description": "desc1"}]
        }
        
        with patch('configurator.utils.file_io.FileIO.get_document') as mock_get_document:
            mock_get_document.return_value = test_data
            
            # Act
            enum = Enumerations("test.yaml")
            
            # Assert
            self.assertEqual(enum.name, "test_enum")
            self.assertEqual(len(enum.values), 1)
            self.assertEqual(enum.values[0]["value"], "value1")

    def test_init_with_invalid_data_raises(self):
        """Test Enumerations initialization with invalid data raises exception."""
        # Arrange
        with patch('configurator.utils.file_io.FileIO.get_document') as mock_get_document:
            event = ConfiguratorEvent("ENU-01", "INIT")
            mock_get_document.side_effect = ConfiguratorException("File not found", event)
            
            # Act & Assert
            with self.assertRaises(ConfiguratorException):
                Enumerations("invalid.yaml")

    def test_init_with_valid_data(self):
        """Test Enumerations initialization with valid data."""
        # Arrange
        test_data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"},
                {"value": "value2", "description": "desc2"}
            ]
        }
        
        with patch('configurator.utils.file_io.FileIO.get_document') as mock_get_document:
            mock_get_document.return_value = test_data
            
            # Act
            enum = Enumerations("test.yaml")
            
            # Assert
            self.assertEqual(enum.name, "test_enum")
            self.assertEqual(len(enum.values), 2)
            self.assertEqual(enum.values[0]["value"], "value1")
            self.assertEqual(enum.values[1]["value"], "value2")

    def test_get_enum_dict(self):
        """Test get_enum_dict method."""
        # Arrange
        test_data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"},
                {"value": "value2", "description": "desc2"}
            ]
        }
        
        with patch('configurator.utils.file_io.FileIO.get_document') as mock_get_document:
            mock_get_document.return_value = test_data
            
            # Act
            enum = Enumerations("test.yaml")
            result = enum.get_enum_dict()
            
            # Assert
            expected = {"value1": "desc1", "value2": "desc2"}
            self.assertEqual(result, expected)

    def test_get_enum_values(self):
        """Test get_enum_values method."""
        # Arrange
        test_data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"},
                {"value": "value2", "description": "desc2"}
            ]
        }
        
        with patch('configurator.utils.file_io.FileIO.get_document') as mock_get_document:
            mock_get_document.return_value = test_data
            
            # Act
            enum = Enumerations("test.yaml")
            result = enum.get_enum_values("test_enum")
            
            # Assert
            expected = {"value1", "value2"}
            self.assertEqual(set(result), expected)

    def test_get_enum_values_enum_not_found(self):
        """Test get_enum_values when enum name is not found."""
        # Arrange
        test_data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"}
            ]
        }
        
        with patch('configurator.utils.file_io.FileIO.get_document') as mock_get_document:
            mock_get_document.return_value = test_data
            
            # Act
            enum = Enumerations("test.yaml")
            result = enum.get_enum_values("nonexistent")
            
            # Assert
            self.assertEqual(result, {"value1"})

    def test_to_dict(self):
        """Test to_dict method."""
        # Arrange
        test_data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"}
            ]
        }
        
        with patch('configurator.utils.file_io.FileIO.get_document') as mock_get_document:
            mock_get_document.return_value = test_data
            
            # Act
            enum = Enumerations("test.yaml")
            result = enum.to_dict()
            
            # Assert
            expected = {
                "file_name": "test.yaml",
                "_locked": False,
                "name": "test_enum",
                "values": [{"value": "value1", "description": "desc1"}]
            }
            self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main() 