import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from flask import Flask
from configurator.routes.type_routes import create_type_routes
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.utils.config import Config


class TestTypeRoutes(unittest.TestCase):
    """Test cases for type routes."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear Config singleton to ensure clean state
        Config._instance = None
        # Store original INPUT_FOLDER if it exists
        self._original_input_folder = os.environ.get('INPUT_FOLDER')
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        
        self.app = Flask(__name__)
        self.app.register_blueprint(create_type_routes(), url_prefix='/api/types')
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
        self.app.register_blueprint(create_type_routes(), url_prefix='/api/types')
        self.client = self.app.test_client()

    @patch('configurator.routes.type_routes.FileIO')
    def test_get_types_success(self, mock_file_io):
        """Test successful GET /api/types."""
        # Arrange
        # Create mock File objects with to_dict() method
        mock_file1 = Mock()
        mock_file1.to_dict.return_value = {"name": "type1.yaml"}
        mock_file2 = Mock()
        mock_file2.to_dict.return_value = {"name": "type2.yaml"}
        mock_files = [mock_file1, mock_file2]
        mock_file_io.get_documents.return_value = mock_files

        # Act
        response = self.client.get('/api/types/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        # For successful responses, expect data directly, not wrapped in event envelope
        self.assertEqual(response_data, [{"name": "type1.yaml"}, {"name": "type2.yaml"}])

    @patch('configurator.routes.type_routes.FileIO')
    def test_get_types_general_exception(self, mock_file_io):
        """Test GET /api/types when FileIO raises a general exception."""
        # Arrange
        mock_file_io.get_documents.side_effect = Exception("Unexpected error")

        # Act
        response = self.client.get('/api/types/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.type_routes.Type')
    def test_get_type_success(self, mock_type_class):
        """Test successful GET /api/types/<file_name>."""
        # Arrange
        mock_type = Mock()
        mock_type.to_dict.return_value = {"name": "test_type", "_locked": False, "version": "1.0.0"}
        mock_type_class.return_value = mock_type

        # Act
        response = self.client.get('/api/types/test_type/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertEqual(response_data, {"name": "test_type", "_locked": False, "version": "1.0.0"})

    @patch('configurator.routes.type_routes.Type')
    def test_get_type_general_exception(self, mock_type_class):
        """Test GET /api/types/<file_name> when Type raises a general exception."""
        # Arrange
        mock_type_class.side_effect = Exception("Unexpected error")

        # Act
        response = self.client.get('/api/types/test_type/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.type_routes.Type')
    def test_update_type_success(self, mock_type_class):
        """Test successful PUT /api/types/<file_name>."""
        # Arrange
        self._setup_config_for_local()
        test_data = {"name": "test_type", "version": "1.0.0"}
        mock_type = Mock()
        mock_saved_file = {"name": "test_type.yaml", "path": "/path/to/test_type.yaml"}
        mock_type.save.return_value = mock_saved_file
        mock_type_class.return_value = mock_type

        # Act
        response = self.client.put('/api/types/test_type/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertEqual(response_data, {"name": "test_type.yaml", "path": "/path/to/test_type.yaml"})

    @patch('configurator.routes.type_routes.Type')
    def test_update_type_general_exception(self, mock_type_class):
        """Test PUT /api/types/<file_name> when Type raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_type_class.side_effect = Exception("Unexpected error")
        test_data = {"name": "test_type", "version": "1.0.0"}

        # Act
        response = self.client.put('/api/types/test_type/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.type_routes.Type')
    def test_delete_type_success(self, mock_type_class):
        """Test successful DELETE /api/types/<file_name>."""
        # Arrange
        self._setup_config_for_local()
        mock_type = Mock()
        mock_event = Mock()
        mock_event.to_dict.return_value = {"deleted": True}
        mock_type.delete.return_value = mock_event
        mock_type_class.return_value = mock_type

        # Act
        response = self.client.delete('/api/types/test_type/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertEqual(response_data, {"deleted": True})

    @patch('configurator.routes.type_routes.Type')
    def test_delete_type_general_exception(self, mock_type_class):
        """Test DELETE /api/types/<file_name> when Type raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_type = Mock()
        mock_type.delete.side_effect = Exception("Unexpected error")
        mock_type_class.return_value = mock_type

        # Act
        response = self.client.delete('/api/types/test_type/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    # Lock/unlock tests removed as functionality was removed

    @patch('configurator.routes.type_routes.Type')
    def test_lock_all_types(self, mock_type_class):
        """Test locking all types."""
        # Arrange
        self._setup_config_for_local()
        mock_event = ConfiguratorEvent("TYP-04", "LOCK_ALL_TYPES")
        mock_event.data = {
            "total_files": 2,
            "operation": "lock_all"
        }
        mock_event.record_success()
        mock_type_class.lock_all.return_value = mock_event

        # Act
        response = self.client.patch('/api/types/')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertIn('type', data)
        self.assertIn('status', data)
        self.assertIn('sub_events', data)
        self.assertIn('data', data)
        self.assertIn('total_files', data['data'])
        self.assertIn('operation', data['data'])


if __name__ == '__main__':
    unittest.main()