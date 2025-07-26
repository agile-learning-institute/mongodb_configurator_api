import unittest
from unittest.mock import patch, MagicMock, Mock
from configurator.services.enumerators import Enumerators
from configurator.services.enumeration_service import Enumerations
import os
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.utils.config import Config


class TestEnumerations(unittest.TestCase):
    """Focused unit tests for Enumerations service class"""

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

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_init(self, mock_get_document):
        """Test Enumerations initialization"""
        mock_get_document.return_value = self.test_enumeration
        
        enum = Enumerations("test.yaml")
        self.assertEqual(enum.name, "test_enum")
        self.assertEqual(len(enum.values), 3)
        self.assertFalse(enum._locked)
        self.assertEqual(enum.values[0]["value"], "value1")
        self.assertEqual(enum.values[0]["description"], "First value")

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_init_defaults(self, mock_get_document):
        """Test Enumerations initialization with defaults"""
        mock_get_document.return_value = {}
        
        enum = Enumerations("test.yaml")
        self.assertIsNone(enum.name)
        self.assertEqual(len(enum.values), 0)
        self.assertFalse(enum._locked)

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_to_dict(self, mock_get_document):
        """Test Enumerations to_dict method"""
        mock_get_document.return_value = self.test_enumeration
        
        enum = Enumerations("test.yaml")
        result = enum.to_dict()
        expected = {
            "_locked": False,
            "file_name": "test.yaml",
            "name": "test_enum",
            "values": [
                {"value": "value1", "description": "First value"},
                {"value": "value2", "description": "Second value"},
                {"value": "value3", "description": "Third value"}
            ]
        }
        self.assertEqual(result, expected)

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_get_enum_dict(self, mock_get_document):
        """Test Enumerations get_enum_dict method"""
        mock_get_document.return_value = self.test_enumeration
        
        enum = Enumerations("test.yaml")
        result = enum.get_enum_dict()
        expected = {
            "value1": "First value",
            "value2": "Second value", 
            "value3": "Third value"
        }
        self.assertEqual(result, expected)

    @patch('configurator.utils.file_io.FileIO.get_document')
    def test_enumerations_get_enum_values(self, mock_get_document):
        """Test Enumerations get_enum_values method"""
        mock_get_document.return_value = self.test_enumeration
        
        enum = Enumerations("test.yaml")
        result = enum.get_enum_values("test_enum")
        expected = {"value1", "value2", "value3"}
        self.assertEqual(set(result), expected)


class TestEnumerators(unittest.TestCase):
    """Focused unit tests for Enumerators helper class"""

    def setUp(self):
        """Set up test environment"""
        self.test_files = [
            Mock(file_name="test1.yaml"),
            Mock(file_name="test2.yaml")
        ]

    @patch('configurator.services.enumerators.FileIO.get_documents')
    @patch('configurator.services.enumerators.Enumerations')
    def test_init_loads_all_enumerations(self, mock_enumerations, mock_get_documents):
        """Test Enumerators initialization loads all enumeration files"""
        mock_get_documents.return_value = self.test_files
        mock_enum1 = Mock()
        mock_enum2 = Mock()
        mock_enumerations.side_effect = [mock_enum1, mock_enum2]
        
        enumerators = Enumerators()
        
        self.assertEqual(len(enumerators.enumerations), 2)
        self.assertEqual(enumerators.enumerations[0], mock_enum1)
        self.assertEqual(enumerators.enumerations[1], mock_enum2)
        mock_enumerations.assert_any_call("test1.yaml")
        mock_enumerations.assert_any_call("test2.yaml")

    @patch('configurator.services.enumerators.FileIO.get_documents')
    @patch('configurator.services.enumerators.Enumerations')
    def test_get_version_finds_version(self, mock_enumerations, mock_get_documents):
        """Test get_version finds the correct version"""
        mock_get_documents.return_value = self.test_files
        mock_enum = Mock()
        mock_enum.version_str = "1.0.0"
        mock_enumerations.return_value = mock_enum
        
        enumerators = Enumerators()
        result = enumerators.get_version("1.0.0")
        
        self.assertEqual(result, mock_enum)

    @patch('configurator.services.enumerators.FileIO.get_documents')
    @patch('configurator.services.enumerators.Enumerations')
    def test_get_version_not_found(self, mock_enumerations, mock_get_documents):
        """Test get_version when version is not found"""
        mock_get_documents.return_value = self.test_files
        mock_enum = Mock()
        mock_enum.version_str = "1.0.0"
        mock_enumerations.return_value = mock_enum
        
        enumerators = Enumerators()
        with self.assertRaises(ConfiguratorException):
            enumerators.get_version("999.0.0")

    @patch('configurator.services.enumerators.FileIO.get_documents')
    def test_init_with_file_io_exception(self, mock_get_documents):
        """Test Enumerators initialization when FileIO raises exception"""
        event = ConfiguratorEvent("ENU-01", "INIT")
        mock_get_documents.side_effect = ConfiguratorException("File error", event)
        
        with self.assertRaises(ConfiguratorException):
            Enumerators()


if __name__ == '__main__':
    unittest.main() 