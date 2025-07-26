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

    @patch('configurator.services.enumerator_service.FileIO')
    @patch('configurator.services.enumerator_service.Enumerations')
    def test_init_with_file_name(self, mock_enumerations, mock_file_io):
        """Test Enumerators initialization with file name"""
        # Arrange
        mock_file_io.get_document.return_value = self.test_document
        mock_enum_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enum_instances
        
        # Act
        enumerators = Enumerators(self.test_file_name)
        
        # Assert
        self.assertEqual(enumerators.file_name, self.test_file_name)
        self.assertFalse(enumerators._locked)
        self.assertEqual(enumerators.version, 1)
        self.assertEqual(len(enumerators.enumerations), 2)
        self.assertEqual(mock_enumerations.call_count, 2)
        mock_file_io.get_document.assert_called_once()

    @patch('configurator.services.enumerator_service.Enumerations')
    def test_init_with_document(self, mock_enumerations):
        """Test Enumerators initialization with document"""
        # Arrange
        mock_enum_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enum_instances
        
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
        
        self.assertIn("Enumerator file name is required", str(context.exception))

    @patch('configurator.services.enumerator_service.Enumerations')
    def test_to_dict(self, mock_enumerations):
        """Test Enumerators to_dict method"""
        # Arrange
        mock_enum1 = Mock()
        mock_enum1.to_dict.return_value = {"name": "enum1", "values": []}
        mock_enum2 = Mock()
        mock_enum2.to_dict.return_value = {"name": "enum2", "values": []}
        mock_enumerations.side_effect = [mock_enum1, mock_enum2]
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        
        # Act
        result = enumerators.to_dict()
        
        # Assert
        expected = {
            "file_name": self.test_file_name,
            "_locked": False,
            "enumerations": [
                {"name": "enum1", "values": []},
                {"name": "enum2", "values": []}
            ]
        }
        self.assertEqual(result, expected)
        mock_enum1.to_dict.assert_called_once()
        mock_enum2.to_dict.assert_called_once()

    @patch('configurator.services.enumerator_service.FileIO')
    @patch('configurator.services.enumerator_service.Enumerations')
    def test_save(self, mock_enumerations, mock_file_io):
        """Test Enumerators save method"""
        # Arrange
        mock_enum_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enum_instances
        mock_file_io.put_document.return_value = {"saved": "document"}
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        
        # Act
        result = enumerators.save()
        
        # Assert
        self.assertEqual(result, {"saved": "document"})
        mock_file_io.put_document.assert_called_once()

    @patch('configurator.services.enumerator_service.FileIO')
    @patch('configurator.services.enumerator_service.Enumerations')
    def test_delete_unlocked_enumerators(self, mock_enumerations, mock_file_io):
        """Test Enumerators delete method for unlocked enumerators"""
        # Arrange
        mock_enum_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enum_instances
        mock_file_io.delete_document.return_value = True
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        enumerators._locked = False
        
        # Act
        result = enumerators.delete()
        
        # Assert
        self.assertTrue(result)
        mock_file_io.delete_document.assert_called_once()

    @patch('configurator.services.enumerator_service.Enumerations')
    def test_delete_locked_enumerators(self, mock_enumerations):
        """Test Enumerators delete method for locked enumerators raises exception"""
        # Arrange
        mock_enum_instances = [Mock(), Mock()]
        mock_enumerations.side_effect = mock_enum_instances
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        enumerators._locked = True
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            enumerators.delete()
        
        self.assertIn("Cannot delete locked enumerator", str(context.exception))

    @patch('configurator.services.enumerator_service.Enumerations')
    def test_get_version_success(self, mock_enumerations):
        """Test Enumerators getVersion method success"""
        # Arrange
        mock_enum1 = Mock()
        mock_enum1.version = 1
        mock_enum2 = Mock()
        mock_enum2.version = 2
        mock_enumerations.side_effect = [mock_enum1, mock_enum2]
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        
        # Act
        result = enumerators.getVersion(2)
        
        # Assert
        self.assertEqual(result, mock_enum2)

    @patch('configurator.services.enumerator_service.Enumerations')
    def test_get_version_not_found(self, mock_enumerations):
        """Test Enumerators getVersion method when version not found"""
        # Arrange
        mock_enum_instances = [Mock(), Mock()]
        mock_enum_instances[0].version = 1
        mock_enum_instances[1].version = 2
        mock_enumerations.side_effect = mock_enum_instances
        
        enumerators = Enumerators(self.test_file_name, self.test_document)
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            enumerators.getVersion(3)
        
        self.assertIn("Version 3 not found", str(context.exception))

    @patch('configurator.services.enumerator_service.FileIO')
    @patch('configurator.services.enumerator_service.Enumerators')
    def test_lock_all_enumerators_success(self, mock_enumerators_class, mock_file_io):
        """Test Enumerators.lock_all method success"""
        # Arrange
        mock_files = [Mock(file_name="enum1.yaml"), Mock(file_name="enum2.yaml")]
        mock_file_io.get_documents.return_value = mock_files
        
        mock_enum1 = Mock()
        mock_enum2 = Mock()
        mock_enumerators_class.side_effect = [mock_enum1, mock_enum2]
        
        # Note: The source code has a potential defect:
        # It has UnboundLocalError with file_event in exception handlers
        # This defect is intermittent and depends on specific error conditions
        # The current test scenario doesn't trigger it, but it exists in the code
        
        # Act
        result = Enumerators.lock_all(True)
        
        # Assert
        self.assertIsNotNone(result)
        # Verify that the method processes the files correctly
        self.assertEqual(mock_enumerators_class.call_count, 2)

    @patch('configurator.services.enumerator_service.FileIO')
    @patch('configurator.services.enumerator_service.Enumerators')
    def test_lock_all_enumerators_failure(self, mock_enumerators_class, mock_file_io):
        """Test Enumerators.lock_all method failure"""
        # Arrange
        mock_files = [Mock(file_name="enum1.yaml")]
        mock_file_io.get_documents.return_value = mock_files
        
        test_event = ConfiguratorEvent(event_id="TEST-01", event_type="TEST_ERROR")
        mock_enumerators_class.side_effect = ConfiguratorException("Test error", test_event)
        
        # Note: The source code has a potential defect:
        # It has UnboundLocalError with file_event in exception handlers
        # This defect is intermittent and depends on specific error conditions
        # The current test scenario triggers ConfiguratorException, not UnboundLocalError
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            Enumerators.lock_all(True)
        
        # Should fail due to ConfiguratorException from the mocked Enumerators constructor
        self.assertIn("Cannot lock all enumerators", str(context.exception))


if __name__ == '__main__':
    unittest.main() 