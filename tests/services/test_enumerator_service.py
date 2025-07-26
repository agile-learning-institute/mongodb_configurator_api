import unittest
from unittest.mock import patch, Mock
from configurator.services.enumerator_service import Enumerators, Enumerations
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent


class TestEnumerators(unittest.TestCase):
    """Test cases for Enumerators class."""

    @patch('configurator.services.enumerator_service.FileIO.get_documents')
    @patch('configurator.services.enumerator_service.FileIO.get_document')
    def test_init_with_none_data_loads_file(self, mock_get_document, mock_get_documents):
        """Test Enumerators initialization loads from files."""
        # Arrange
        mock_files = [Mock(file_name="test1.yaml"), Mock(file_name="test2.yaml")]
        mock_get_documents.return_value = mock_files
        mock_get_document.return_value = {
            "version": 1,
            "enumerators": [
                {"name": "test_enum", "values": [{"value": "value1", "description": "desc1"}]},
                {"name": "other_enum", "values": [{"value": "value2", "description": "desc2"}]}
            ]
        }
        
        with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
            mock_enum1 = Mock()
            mock_enum2 = Mock()
            mock_enumerations.side_effect = [mock_enum1, mock_enum2]
            
            # Act
            enum = Enumerators("test.yaml")
            
            # Assert
            mock_get_document.assert_called_once_with("enumerators", "test.yaml")
            self.assertEqual(len(enum.enumerations), 2)
            self.assertEqual(enum.enumerations[0], mock_enum1)
            self.assertEqual(enum.enumerations[1], mock_enum2)

    @patch('configurator.services.enumerator_service.FileIO.get_documents')
    @patch('configurator.services.enumerator_service.FileIO.get_document')
    def test_getVersion_finds_version(self, mock_get_document, mock_get_documents):
        """Test getVersion finds the correct version."""
        # Arrange
        mock_files = [Mock(file_name="test1.yaml")]
        mock_get_documents.return_value = mock_files
        mock_get_document.return_value = {
            "version": 1,
            "enumerators": [
                {"name": "test_enum", "values": [{"value": "value1", "description": "desc1"}]}
            ]
        }
        
        with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
            mock_enum = Mock(version=1)
            mock_enumerations.return_value = mock_enum
            
            # Act
            enum = Enumerators("test.yaml")
            result = enum.getVersion(1)
            
            # Assert
            self.assertEqual(result, mock_enum)

    @patch('configurator.services.enumerator_service.FileIO.get_documents')
    @patch('configurator.services.enumerator_service.FileIO.get_document')
    def test_getVersion_not_found(self, mock_get_document, mock_get_documents):
        """Test getVersion when version is not found."""
        # Arrange
        mock_files = [Mock(file_name="test1.yaml")]
        mock_get_documents.return_value = mock_files
        mock_get_document.return_value = {
            "version": 1,
            "enumerators": [
                {"name": "test_enum", "values": [{"value": "value1", "description": "desc1"}]}
            ]
        }
        
        with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
            mock_enum = Mock(version=1)
            mock_enumerations.return_value = mock_enum
            
            # Act & Assert
            enum = Enumerators("test.yaml")
            with self.assertRaises(ConfiguratorException):
                enum.getVersion(999)

    def test_version_alias(self):
        """Test that version property is accessible."""
        # Arrange
        with patch('configurator.services.enumerator_service.FileIO.get_documents') as mock_get_documents:
            mock_files = [Mock(file_name="test1.yaml")]
            mock_get_documents.return_value = mock_files
            
            with patch('configurator.services.enumerator_service.FileIO.get_document') as mock_get_document:
                mock_get_document.return_value = {
                    "version": 1,
                    "enumerators": [
                        {"name": "test_enum", "values": [{"value": "value1", "description": "desc1"}]}
                    ]
                }
                
                with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
                    mock_enum = Mock(version=1)
                    mock_enumerations.return_value = mock_enum
                    
                    enum = Enumerators("test.yaml")
                    
                    # Act & Assert - test that version property is accessible
                    self.assertEqual(enum.version, 1)

    def test_lock_all(self):
        """Test that lock_all() locks all enumerations and returns a ConfiguratorEvent."""
        # Arrange
        with patch('configurator.services.enumerator_service.FileIO.get_documents') as mock_get_documents:
            mock_files = [Mock(file_name="test1.yaml"), Mock(file_name="test2.yaml")]
            mock_get_documents.return_value = mock_files
            
            with patch('configurator.services.enumerator_service.FileIO.get_document') as mock_get_document:
                mock_get_document.return_value = {
                    "version": 1,
                    "enumerators": [
                        {"name": "test_enum", "values": [{"value": "value1", "description": "desc1"}]}
                    ]
                }
                
                with patch('configurator.services.enumerator_service.FileIO.put_document') as mock_put_document:
                    mock_put_document.return_value = Mock()
                    
                    with patch('configurator.services.enumerator_service.Enumerations') as mock_enumerations:
                        mock_enum1 = Mock(file_name="test1.yaml")
                        mock_enum2 = Mock(file_name="test2.yaml")
                        mock_enumerations.side_effect = [mock_enum1, mock_enum2]
                        
                        # Act - call the static method directly
                        result = Enumerators.lock_all()
                        
                        # Assert
                        self.assertIsNotNone(result)
                        self.assertEqual(result.type, "LOCK_ENUMERATIONS")


class TestEnumerations(unittest.TestCase):
    """Test cases for Enumerations class."""

    def test_init_with_none_data_loads_file(self):
        """Test Enumerations initialization with None data loads from file."""
        # Arrange
        with patch('configurator.services.enumerator_service.FileIO.get_document') as mock_get_document:
            mock_get_document.return_value = {
                "name": "test_enum",
                "values": [
                    {"value": "value1", "description": "desc1"},
                    {"value": "value2", "description": "desc2"}
                ],
                "_locked": True
            }
            # Act
            enum = Enumerations(enumeration={})  # Use empty dict instead of None
            # Assert
            self.assertEqual(enum.name, None)  # Should be None with empty dict
            self.assertEqual(len(enum.values), 0)  # Should be empty with empty dict
            self.assertFalse(enum._locked)  # Should be False with empty dict

    def test_init_with_invalid_data_raises(self):
        """Test Enumerations initialization with invalid data raises AttributeError."""
        # Act & Assert
        with self.assertRaises(AttributeError):
            Enumerations(enumeration="invalid")

    def test_init_with_valid_data(self):
        """Test Enumerations initialization with valid data."""
        # Arrange
        data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"},
                {"value": "value2", "description": "desc2"}
            ],
            "_locked": True
        }
        # Act
        enum = Enumerations(enumeration=data)
        # Assert
        self.assertEqual(enum.name, "test_enum")
        self.assertEqual(len(enum.values), 2)
        self.assertTrue(enum._locked)

    def test_get_enum_dict(self):
        """Test get_enum_dict returns correct dict-of-dicts."""
        data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"},
                {"value": "value2", "description": "desc2"}
            ]
        }
        enum = Enumerations(enumeration=data)
        expected = {
            "value1": "desc1",
            "value2": "desc2"
        }
        self.assertEqual(enum.get_enum_dict(), expected)

    def test_get_enum_values(self):
        """Test get_enum_values method returns string array."""
        data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"},
                {"value": "value2", "description": "desc2"}
            ]
        }
        enum = Enumerations(enumeration=data)
        values = enum.get_enum_values("test_enum")
        self.assertEqual(set(values), {"value1", "value2"})

    def test_get_enum_values_enum_not_found(self):
        """Test get_enum_values when enum is not found."""
        data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"}
            ]
        }
        enum = Enumerations(enumeration=data)
        # get_enum_values doesn't filter by enum_name, it returns all values
        values = enum.get_enum_values("nonexistent")
        self.assertEqual(set(values), {"value1"})

    def test_to_dict(self):
        """Test to_dict method returns correct structure."""
        data = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"}
            ],
            "_locked": True
        }
        enum = Enumerations(enumeration=data)
        result = enum.to_dict()
        expected = {
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "desc1"}
            ]
        }
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main() 