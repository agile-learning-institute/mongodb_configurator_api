import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from flask import Flask
from configurator.routes.enumerator_routes import create_enumerator_routes
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.utils.config import Config


class TestEnumeratorRoutes(unittest.TestCase):
    """Test cases for enumerator routes."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear Config singleton to ensure clean state
        Config._instance = None
        # Store original INPUT_FOLDER if it exists
        self._original_input_folder = os.environ.get('INPUT_FOLDER')
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        
        self.app = Flask(__name__)
        self.app.register_blueprint(create_enumerator_routes(), url_prefix='/api/enumerations')
        self.client = self.app.test_client()
        self.temp_dir = None

    def tearDown(self):
        """Clean up after tests."""
        # Restore original INPUT_FOLDER
        if self._original_input_folder:
            os.environ['INPUT_FOLDER'] = self._original_input_folder
        elif 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        # Clear Config singleton
        Config._instance = None
        # Clean up temp directory if created
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def _setup_config_for_local(self):
        """Set up Config with BUILT_AT from file with value 'Local' for write operations."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        # Create api_config directory
        api_config_dir = Path(self.temp_dir) / "api_config"
        api_config_dir.mkdir()
        # Create BUILT_AT file with value "Local"
        built_at_file = api_config_dir / "BUILT_AT"
        built_at_file.write_text("Local")
        # Create MONGODB_REQUIRE_TLS file with value "false"
        require_tls_file = api_config_dir / "MONGODB_REQUIRE_TLS"
        require_tls_file.write_text("false")
        # Set INPUT_FOLDER environment variable
        os.environ['INPUT_FOLDER'] = self.temp_dir
        # Clear and reinitialize Config
        Config._instance = None
        # Recreate blueprint with new Config
        self.app = Flask(__name__)
        self.app.register_blueprint(create_enumerator_routes(), url_prefix='/api/enumerations')
        self.client = self.app.test_client()

    @patch('configurator.routes.enumerator_routes.FileIO.get_documents')
    def test_get_enumerations_success(self, mock_get_documents):
        """Test successful GET /api/enumerations - Get enumeration files."""
        # Arrange
        mock_files = [
            Mock(file_name="test1.yaml", to_dict=lambda: {"name": "test1.yaml", "path": "/path/to/test1.yaml"}),
            Mock(file_name="test2.yaml", to_dict=lambda: {"name": "test2.yaml", "path": "/path/to/test2.yaml"})
        ]
        mock_get_documents.return_value = mock_files
        
        # Act
        response = self.client.get('/api/enumerations/')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]["name"], "test1.yaml")
        self.assertEqual(response_data[1]["name"], "test2.yaml")

    @patch('configurator.routes.enumerator_routes.FileIO.get_documents')
    def test_get_enumerations_exception(self, mock_get_documents):
        """Test GET /api/enumerations when FileIO raises exception."""
        # Arrange
        mock_get_documents.side_effect = Exception("File error")

        # Act
        response = self.client.get('/api/enumerations/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.enumerator_routes.Enumerations')
    def test_get_enumeration_success(self, mock_enumerations_class):
        """Test successful GET /api/enumerations/{name} - Get specific enumeration."""
        # Arrange
        mock_enumeration = Mock()
        mock_enumeration.to_dict.return_value = {
            "version": 1,
            "enumerators": {"test_enum": {"value1": True}},
            "file_name": "test"
        }
        mock_enumerations_class.return_value = mock_enumeration
        
        # Act
        response = self.client.get('/api/enumerations/test/')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertEqual(response_data["version"], 1)
        self.assertEqual(response_data["enumerators"], {"test_enum": {"value1": True}})
        mock_enumerations_class.assert_called_once_with(file_name="test")

    @patch('configurator.routes.enumerator_routes.Enumerations')
    def test_get_enumeration_exception(self, mock_enumerations_class):
        """Test GET /api/enumerations/{name} when Enumerations raises exception."""
        # Arrange
        event = ConfiguratorEvent("ENU-02", "GET_ENUMERATION")
        mock_enumerations_class.side_effect = ConfiguratorException("File not found", event)

        # Act
        response = self.client.get('/api/enumerations/test/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.enumerator_routes.Enumerations')
    def test_put_enumeration_success(self, mock_enumerations_class):
        """Test successful PUT /api/enumerations/{name} - Update specific enumeration."""
        # Arrange
        self._setup_config_for_local()
        test_data = {
            "version": 1,
            "enumerators": {"test_enum": {"value1": True}},
            "file_name": "test"
        }
        mock_enumeration = Mock()
        mock_enumeration.to_dict.return_value = test_data
        mock_enumeration.save.return_value = {"saved": "data"}
        mock_enumerations_class.return_value = mock_enumeration

        # Act
        response = self.client.put('/api/enumerations/test/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertEqual(response_data, {"saved": "data"})
        mock_enumerations_class.assert_called_once_with("test", test_data)

    @patch('configurator.routes.enumerator_routes.Enumerations')
    def test_put_enumeration_exception(self, mock_enumerations_class):
        """Test PUT /api/enumerations/{name} when Enumerations raises exception."""
        # Arrange
        self._setup_config_for_local()
        event = ConfiguratorEvent("ENU-03", "PUT_ENUMERATION")
        mock_enumerations_class.side_effect = ConfiguratorException("Save error", event)
        test_data = {"version": 1, "enumerators": {}, "file_name": "test"}

        # Act
        response = self.client.put('/api/enumerations/test/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.enumerator_routes.Enumerations')
    def test_lock_enumerations_success(self, mock_enumerations_class):
        """Test successful PATCH /api/enumerations - Lock all enumerations."""
        # Arrange
        self._setup_config_for_local()
        mock_event = Mock()
        mock_event.to_dict.return_value = {
            "id": "ENU-04",
            "type": "LOCK_ENUMERATIONS",
            "status": "SUCCESS",
            "data": {},
            "events": []
        }
        mock_enumerations_class.lock_all.return_value = mock_event

        # Act
        response = self.client.patch('/api/enumerations/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertEqual(response_data["status"], "SUCCESS")
        mock_enumerations_class.lock_all.assert_called_once()

    @patch('configurator.routes.enumerator_routes.Enumerations')
    def test_lock_enumerations_exception(self, mock_enumerations_class):
        """Test PATCH /api/enumerations when Enumerations raises exception."""
        # Arrange
        self._setup_config_for_local()
        event = ConfiguratorEvent("ENU-04", "LOCK_ENUMERATIONS")
        mock_enumerations_class.lock_all.side_effect = ConfiguratorException("Lock error", event)

        # Act
        response = self.client.patch('/api/enumerations/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    def test_enumerations_with_filename_not_allowed(self):
        """Test that enumerations with filename is not allowed."""
        # Act
        response = self.client.get('/api/enumerations/test.json')

        # Assert
        self.assertEqual(response.status_code, 308)  # Redirect to trailing slash


if __name__ == '__main__':
    unittest.main()