import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from flask import Flask
from configurator.routes.configuration_routes import create_configuration_routes
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.utils.config import Config


class TestConfigurationRoutes(unittest.TestCase):
    """Test cases for configuration routes."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear Config singleton to ensure clean state
        Config._instance = None
        # Store original INPUT_FOLDER if it exists
        self._original_input_folder = os.environ.get('INPUT_FOLDER')
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        
        self.app = Flask(__name__)
        self.app.register_blueprint(create_configuration_routes(), url_prefix='/api/configurations')
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
        # Set INPUT_FOLDER environment variable
        os.environ['INPUT_FOLDER'] = self.temp_dir
        # Clear and reinitialize Config
        Config._instance = None
        # Recreate blueprint with new Config
        self.app = Flask(__name__)
        self.app.register_blueprint(create_configuration_routes(), url_prefix='/api/configurations')
        self.client = self.app.test_client()

    @patch('configurator.routes.configuration_routes.FileIO')
    def test_list_configurations_success(self, mock_file_io):
        """Test successful GET /api/configurations/."""
        # Arrange
        # Create mock File objects with file_name attribute
        mock_file1 = Mock()
        mock_file1.to_dict.return_value = {"file_name": "config1.yaml", "size": 100, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}
        mock_file2 = Mock()
        mock_file2.to_dict.return_value = {"file_name": "config2.yaml", "size": 200, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}
        mock_files = [mock_file1, mock_file2]
        mock_file_io.get_documents.return_value = mock_files

        # Act
        response = self.client.get('/api/configurations/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        expected_data = [mock_file1.to_dict.return_value, mock_file2.to_dict.return_value]
        self.assertEqual(response_data, expected_data)

    @patch('configurator.routes.configuration_routes.FileIO')
    def test_list_configurations_general_exception(self, mock_file_io):
        """Test GET /api/configurations/ when FileIO raises a general exception."""
        # Arrange
        mock_file_io.get_documents.side_effect = Exception("Unexpected error")

        # Act
        response = self.client.get('/api/configurations/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_process_configurations_success(self, mock_configuration_class):
        """Test successful POST /api/configurations/."""
        # Arrange
        self._setup_config_for_local()
        mock_event = ConfiguratorEvent("CFG-ROUTES-02", "PROCESS_ALL_CONFIGURATIONS")
        mock_event.record_success()
        mock_configuration_class.process_all.return_value = mock_event

        # Act
        response = self.client.post('/api/configurations/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        # For endpoints that return events, expect event envelope structure
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertEqual(response_data["status"], "SUCCESS")
        self.assertIn("sub_events", response_data)

    def test_process_configurations_not_local(self):
        """Test POST /api/configurations/ when not in local mode."""
        # Arrange - Config is in default state (BUILT_AT from default, not from file)
        # Ensure Config is in default state by clearing and reinitializing
        Config._instance = None
        # Recreate blueprint to pick up fresh Config instance
        self.app = Flask(__name__)
        self.app.register_blueprint(create_configuration_routes(), url_prefix='/api/configurations')
        self.client = self.app.test_client()

        # Act
        response = self.client.post('/api/configurations/')

        # Assert
        self.assertEqual(response.status_code, 403)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")
        # Check that the error message is in the sub_events (the actual error from assert_local)
        self.assertIn("sub_events", response_data)
        self.assertGreater(len(response_data["sub_events"]), 0)
        sub_event = response_data["sub_events"][0]
        self.assertIn("data", sub_event)
        self.assertIn("error", sub_event["data"])
        self.assertIn("BUILT_AT", sub_event["data"]["error"])

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_process_configurations_general_exception(self, mock_configuration_class):
        """Test POST /api/configurations/ when Configuration.process_all raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_configuration_class.process_all.side_effect = Exception("Unexpected error")

        # Act
        response = self.client.post('/api/configurations/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_get_configuration_success(self, mock_configuration_class):
        """Test successful GET /api/configurations/<file_name>/."""
        # Arrange
        mock_configuration = Mock()
        mock_configuration.to_dict.return_value = {"name": "test_config", "version": "1.0.0"}
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.get('/api/configurations/test_config/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        # For successful responses, expect data directly, not wrapped in event envelope
        self.assertEqual(response_data, {"name": "test_config", "version": "1.0.0"})

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_get_configuration_general_exception(self, mock_configuration_class):
        """Test GET /api/configurations/<file_name>/ when Configuration raises a general exception."""
        # Arrange
        mock_configuration_class.side_effect = Exception("Unexpected error")

        # Act
        response = self.client.get('/api/configurations/test_config/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_put_configuration_success(self, mock_configuration_class):
        """Test successful PUT /api/configurations/<file_name>/."""
        # Arrange
        self._setup_config_for_local()
        test_data = {"name": "test_config", "version": "1.0.0", "_locked": False}
        mock_configuration = Mock()
        mock_configuration.to_dict.return_value = {"name": "test_config", "version": "1.0.0", "_locked": False}
        mock_configuration.save.return_value = {"name": "test_config", "version": "1.0.0", "_locked": False}
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.put('/api/configurations/test_config/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        # For successful responses, expect the saved data directly
        self.assertEqual(response_data, {"name": "test_config", "version": "1.0.0", "_locked": False})

    def test_put_configuration_not_local(self):
        """Test PUT /api/configurations/<file_name>/ when not in local mode."""
        # Arrange - Config is in default state (BUILT_AT from default, not from file)
        # Ensure Config is in default state by clearing and reinitializing
        Config._instance = None
        # Recreate blueprint to pick up fresh Config instance
        self.app = Flask(__name__)
        self.app.register_blueprint(create_configuration_routes(), url_prefix='/api/configurations')
        self.client = self.app.test_client()
        test_data = {"name": "test_config", "version": "1.0.0"}

        # Act
        response = self.client.put('/api/configurations/test_config/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 403)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")
        # Check that the error message is in the sub_events (the actual error from assert_local)
        self.assertIn("sub_events", response_data)
        self.assertGreater(len(response_data["sub_events"]), 0)
        sub_event = response_data["sub_events"][0]
        self.assertIn("data", sub_event)
        self.assertIn("error", sub_event["data"])
        self.assertIn("BUILT_AT", sub_event["data"]["error"])

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_put_configuration_general_exception(self, mock_configuration_class):
        """Test PUT /api/configurations/<file_name>/ when Configuration raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_configuration_class.side_effect = Exception("Unexpected error")
        test_data = {"name": "test_config", "version": "1.0.0"}

        # Act
        response = self.client.put('/api/configurations/test_config/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_delete_configuration_success(self, mock_configuration_class):
        """Test successful DELETE /api/configurations/<file_name>/."""
        # Arrange
        self._setup_config_for_local()
        mock_configuration = Mock()
        mock_event = Mock()
        mock_event.to_dict.return_value = {
            "id": "CFG-ROUTES-07",
            "type": "DELETE_CONFIGURATION",
            "status": "SUCCESS",
            "data": {},
            "sub_events": []
        }
        mock_configuration.delete.return_value = mock_event
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.delete('/api/configurations/test_config/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "SUCCESS")

    def test_delete_configuration_not_local(self):
        """Test DELETE /api/configurations/<file_name>/ when not in local mode."""
        # Arrange - Config is in default state (BUILT_AT from default, not from file)
        # Ensure Config is in default state by clearing and reinitializing
        Config._instance = None
        # Recreate blueprint to pick up fresh Config instance
        self.app = Flask(__name__)
        self.app.register_blueprint(create_configuration_routes(), url_prefix='/api/configurations')
        self.client = self.app.test_client()

        # Act
        response = self.client.delete('/api/configurations/test_config/')

        # Assert
        self.assertEqual(response.status_code, 403)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")
        # Check that the error message is in the sub_events (the actual error from assert_local)
        self.assertIn("sub_events", response_data)
        self.assertGreater(len(response_data["sub_events"]), 0)
        sub_event = response_data["sub_events"][0]
        self.assertIn("data", sub_event)
        self.assertIn("error", sub_event["data"])
        self.assertIn("BUILT_AT", sub_event["data"]["error"])

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_delete_configuration_general_exception(self, mock_configuration_class):
        """Test DELETE /api/configurations/<file_name>/ when Configuration raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_configuration = Mock()
        mock_configuration.delete.side_effect = Exception("Unexpected error")
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.delete('/api/configurations/test_config/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_lock_unlock_configuration_success(self, mock_configuration_class):
        """Test successful PATCH /api/configurations/<file_name>/ - removed as no longer supported."""
        # This test is no longer applicable as we removed lock/unlock functionality
        pass

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_lock_unlock_configuration_general_exception(self, mock_configuration_class):
        """Test PATCH /api/configurations/<file_name>/ when Configuration raises a general exception - removed as no longer supported."""
        # This test is no longer applicable as we removed lock/unlock functionality
        pass

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_process_configuration_success(self, mock_configuration_class):
        """Test successful POST /api/configurations/<file_name>/."""
        # Arrange
        self._setup_config_for_local()
        mock_event = ConfiguratorEvent("CFG-ROUTES-02", "PROCESS_ALL_CONFIGURATIONS")
        mock_event.record_success()
        mock_configuration_class.process_one.return_value = mock_event
        
        # Act
        response = self.client.post('/api/configurations/test_config/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn("status", response_data)
        self.assertEqual(response_data["status"], "SUCCESS")

    def test_process_configuration_not_local(self):
        """Test POST /api/configurations/<file_name>/ when not in local mode."""
        # Arrange - Config is in default state (BUILT_AT from default, not from file)
        # Ensure Config is in default state by clearing and reinitializing
        Config._instance = None
        # Recreate blueprint to pick up fresh Config instance
        self.app = Flask(__name__)
        self.app.register_blueprint(create_configuration_routes(), url_prefix='/api/configurations')
        self.client = self.app.test_client()

        # Act
        response = self.client.post('/api/configurations/test_config/')

        # Assert
        self.assertEqual(response.status_code, 403)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")
        # Check that the error message is in the sub_events (the actual error from assert_local)
        self.assertIn("sub_events", response_data)
        self.assertGreater(len(response_data["sub_events"]), 0)
        sub_event = response_data["sub_events"][0]
        self.assertIn("data", sub_event)
        self.assertIn("error", sub_event["data"])
        self.assertIn("BUILT_AT", sub_event["data"]["error"])
        
    @patch('configurator.routes.configuration_routes.Configuration')
    def test_process_configuration_general_exception(self, mock_configuration_class):
        """Test POST /api/configurations/<file_name>/ when Configuration raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_configuration = Mock()
        mock_configuration.process.side_effect = Exception("Unexpected error")
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.post('/api/configurations/test_config/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_get_json_schema_success(self, mock_configuration_class):
        """Test successful GET /api/configurations/json_schema/<file_name>/<version>/."""
        # Arrange
        mock_configuration = Mock()
        mock_configuration.get_json_schema.return_value = {"type": "object"}
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.get('/api/configurations/json_schema/test_config/1.0.0/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        # For successful responses, expect data directly, not wrapped in event envelope
        self.assertEqual(response_data, {"type": "object"})

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_get_json_schema_general_exception(self, mock_configuration_class):
        """Test GET /api/configurations/json_schema/<file_name>/<version>/ when Configuration raises a general exception."""
        # Arrange
        mock_configuration = Mock()
        mock_configuration.get_json_schema.side_effect = Exception("Unexpected error")
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.get('/api/configurations/json_schema/test_config/1.0.0/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_get_bson_schema_success(self, mock_configuration_class):
        """Test successful GET /api/configurations/bson_schema/<file_name>/<version>/."""
        # Arrange
        mock_configuration = Mock()
        mock_configuration.get_bson_schema.return_value = {"type": "object"}
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.get('/api/configurations/bson_schema/test_config/1.0.0/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        # For successful responses, expect data directly, not wrapped in event envelope
        self.assertEqual(response_data, {"type": "object"})

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_get_bson_schema_general_exception(self, mock_configuration_class):
        """Test GET /api/configurations/bson_schema/<file_name>/<version>/ when Configuration raises a general exception."""
        # Arrange
        mock_configuration = Mock()
        mock_configuration.get_bson_schema.side_effect = Exception("Unexpected error")
        mock_configuration_class.return_value = mock_configuration

        # Act
        response = self.client.get('/api/configurations/bson_schema/test_config/1.0.0/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.TemplateService.create_collection')
    def test_create_collection_configurator_exception(self, mock_create_collection):
        """Test POST /api/configurations/collection/<file_name> when TemplateService raises ConfiguratorException."""
        # Arrange
        self._setup_config_for_local()
        event = ConfiguratorEvent("TPL-01", "TEMPLATE_ERROR")
        mock_create_collection.side_effect = ConfiguratorException("Template error", event)

        # Act
        response = self.client.post('/api/configurations/collection/test_collection/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.TemplateService.create_collection')
    def test_create_collection_success(self, mock_create_collection):
        """Test successful POST /api/configurations/collection/<file_name>."""
        # Arrange
        self._setup_config_for_local()
        mock_create_collection.return_value = {"created": True}

        # Act
        response = self.client.post('/api/configurations/collection/test_collection/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        # For successful responses, expect data directly, not wrapped in event envelope
        self.assertEqual(response_data, {"created": True})

    def test_create_collection_not_local(self):
        """Test POST /api/configurations/collection/<file_name> when not in local mode."""
        # Arrange - Config is in default state (BUILT_AT from default, not from file)
        # Ensure Config is in default state by clearing and reinitializing
        Config._instance = None
        # Recreate blueprint to pick up fresh Config instance
        self.app = Flask(__name__)
        self.app.register_blueprint(create_configuration_routes(), url_prefix='/api/configurations')
        self.client = self.app.test_client()

        # Act
        response = self.client.post('/api/configurations/collection/test_collection/')

        # Assert
        self.assertEqual(response.status_code, 403)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")
        # Check that the error message is in the sub_events (the actual error from assert_local)
        self.assertIn("sub_events", response_data)
        self.assertGreater(len(response_data["sub_events"]), 0)
        sub_event = response_data["sub_events"][0]
        self.assertIn("data", sub_event)
        self.assertIn("error", sub_event["data"])
        self.assertIn("BUILT_AT", sub_event["data"]["error"])

    @patch('configurator.routes.configuration_routes.TemplateService.create_collection')
    def test_create_collection_general_exception(self, mock_create_collection):
        """Test POST /api/configurations/collection/<file_name> when TemplateService raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_create_collection.side_effect = Exception("Unexpected error")

        # Act
        response = self.client.post('/api/configurations/collection/test_collection/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.configuration_routes.Configuration')
    def test_lock_all_configurations(self, mock_configuration_class):
        """Test locking all configurations - verifies versions are locked."""
        # Arrange
        self._setup_config_for_local()
        mock_event = ConfiguratorEvent("configurations-03", "LOCK_ALL_CONFIGURATIONS")
        mock_event.data = {
            "total_files": 2,
            "operation": "lock_all"
        }
        mock_event.record_success()
        mock_configuration_class.lock_all.return_value = mock_event

        # Act
        response = self.client.patch('/api/configurations/')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertIn('type', data)
        self.assertIn('status', data)
        self.assertIn('sub_events', data)
        self.assertEqual(data['status'], 'SUCCESS')
        # Verify lock_all was called (defaults to True)
        mock_configuration_class.lock_all.assert_called_once()

    def test_lock_all_configurations_not_local(self):
        """Test PATCH /api/configurations/ when not in local mode."""
        # Arrange - Config is in default state (BUILT_AT from default, not from file)
        # Ensure Config is in default state by clearing and reinitializing
        Config._instance = None
        # Recreate blueprint to pick up fresh Config instance
        self.app = Flask(__name__)
        self.app.register_blueprint(create_configuration_routes(), url_prefix='/api/configurations')
        self.client = self.app.test_client()

        # Act
        response = self.client.patch('/api/configurations/')

        # Assert
        self.assertEqual(response.status_code, 403)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")
        # Check that the error message is in the sub_events (the actual error from assert_local)
        self.assertIn("sub_events", response_data)
        self.assertGreater(len(response_data["sub_events"]), 0)
        sub_event = response_data["sub_events"][0]
        self.assertIn("data", sub_event)
        self.assertIn("error", sub_event["data"])
        self.assertIn("BUILT_AT", sub_event["data"]["error"])


if __name__ == '__main__':
    unittest.main()