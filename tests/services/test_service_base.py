import unittest
from unittest.mock import patch, MagicMock
from configurator.services.service_base import ServiceBase
from configurator.utils.config import Config
from configurator.utils.configurator_exception import ConfiguratorException

class TestService(ServiceBase):
    """Test service class that extends ServiceBase"""
    
    def __init__(self, file_name: str = None, document: dict = None):
        super().__init__(file_name, document, "types")
        self.test_property = self._document.get("test_property", "default")
    
    def to_dict(self):
        d = super().to_dict()
        d["test_property"] = self.test_property
        return d
    
    @staticmethod
    def _get_folder_name():
        return "types"


class TestServiceBase(unittest.TestCase):
    """Test cases for ServiceBase class"""
    
    def setUp(self):
        self.test_file_name = "test.yaml"
        self.test_document = {"test_property": "test_value", "_locked": False}
    
    def test_init_with_file_name(self):
        """Test ServiceBase initialization with file name"""
        with patch('configurator.services.service_base.FileIO.get_document') as mock_get_document:
            mock_get_document.return_value = self.test_document
            service = TestService(self.test_file_name)
            self.assertEqual(service.file_name, self.test_file_name)
            self.assertEqual(service.test_property, "test_value")
            # FileIO.get_document should be called at least once
            mock_get_document.assert_called_with("types", self.test_file_name)
    
    def test_init_with_document(self):
        """Test ServiceBase initialization with document"""
        service = TestService(self.test_file_name, self.test_document)
        self.assertEqual(service.file_name, self.test_file_name)
        self.assertEqual(service.test_property, "test_value")
    
    def test_init_without_file_name(self):
        """Test ServiceBase initialization without file name raises exception"""
        with self.assertRaises(ConfiguratorException) as context:
            TestService()
        self.assertIn("type file name is required", str(context.exception))
    
    def test_to_dict(self):
        """Test ServiceBase to_dict method"""
        service = TestService(self.test_file_name, self.test_document)
        result = service.to_dict()
        self.assertEqual(result["file_name"], self.test_file_name)
        self.assertEqual(result["_locked"], False)
        self.assertEqual(result["test_property"], "test_value")
    
    def test_save(self):
        """Test ServiceBase save method"""
        with patch('configurator.services.service_base.FileIO.put_document') as mock_put_document:
            mock_put_document.return_value = {"saved": True}
            service = TestService(self.test_file_name, self.test_document)
            result = service.save()
            mock_put_document.assert_called_once()
            self.assertEqual(result, {"saved": True})
    
    def test_delete_unlocked(self):
        """Test ServiceBase delete method for unlocked service"""
        with patch('configurator.services.service_base.FileIO.delete_document') as mock_delete_document:
            mock_delete_document.return_value = {"deleted": True}
            service = TestService(self.test_file_name, self.test_document)
            result = service.delete()
            mock_delete_document.assert_called_once()
            self.assertEqual(result, {"deleted": True})
    
    def test_delete_locked(self):
        """Test ServiceBase delete method for locked service raises exception"""
        locked_document = {"test_property": "test_value", "_locked": True}
        service = TestService(self.test_file_name, locked_document)
        with self.assertRaises(ConfiguratorException) as context:
            service.delete()
        self.assertIn("Cannot delete locked type", str(context.exception))
    
    @patch('configurator.services.service_base.FileIO.get_documents')
    @patch('configurator.services.service_base.FileIO.put_document')
    @patch('configurator.services.service_base.FileIO.get_document')
    def test_lock_all_success(self, mock_get_document, mock_put_document, mock_get_documents):
        """Test ServiceBase lock_all method success"""
        mock_file = MagicMock()
        mock_file.file_name = "test.yaml"
        mock_get_documents.return_value = [mock_file]
        mock_get_document.return_value = self.test_document
        mock_put_document.return_value = {"saved": True}
        
        result = ServiceBase.lock_all(TestService)
        
        self.assertIsNotNone(result)
        mock_put_document.assert_called_once()
    
    @patch('configurator.services.service_base.FileIO.get_documents')
    def test_lock_all_failure(self, mock_get_documents):
        """Test ServiceBase lock_all method failure"""
        mock_file = MagicMock()
        mock_file.file_name = "test.yaml"
        mock_get_documents.return_value = [mock_file]
        
        with patch('configurator.services.service_base.FileIO.put_document') as mock_put_document:
            mock_put_document.side_effect = Exception("Test error")
            
            with self.assertRaises(ConfiguratorException) as context:
                ServiceBase.lock_all(TestService)
            self.assertIn("Cannot lock all types", str(context.exception))


if __name__ == '__main__':
    unittest.main() 