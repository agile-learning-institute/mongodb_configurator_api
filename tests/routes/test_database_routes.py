import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from flask import Flask
from configurator.routes.database_routes import create_database_routes
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.utils.config import Config


class TestDatabaseRoutes(unittest.TestCase):
    """Test cases for database routes."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear Config singleton to ensure clean state
        Config._instance = None
        # Store original INPUT_FOLDER if it exists
        self._original_input_folder = os.environ.get('INPUT_FOLDER')
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        
        self.app = Flask(__name__)
        self.app.register_blueprint(create_database_routes(), url_prefix='/api/database')
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
        self.app.register_blueprint(create_database_routes(), url_prefix='/api/database')
        self.client = self.app.test_client()

    @patch('configurator.routes.database_routes.MongoIO')
    def test_drop_database_success(self, mock_mongo_io_class):
        """Test successful DELETE /api/database."""
        # Arrange
        self._setup_config_for_local()
        mock_mongo_io = Mock()
        # Create a mock event that returns a proper to_dict() response
        mock_event = Mock()
        mock_event.to_dict.return_value = {
            "id": "MON-12",
            "type": "DROP_DATABASE", 
            "status": "SUCCESS",
            "data": {"message": "Database Dropped"},
            "starts": "2024-01-01T00:00:00.000Z",
            "ends": "2024-01-01T00:00:00.000Z",
            "sub_events": []
        }
        mock_mongo_io.drop_database.return_value = mock_event
        mock_mongo_io_class.return_value = mock_mongo_io

        # Act
        response = self.client.delete('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        # Expect a single event, not a list
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data["status"], "SUCCESS")
        mock_mongo_io.drop_database.assert_called_once()
        mock_mongo_io.disconnect.assert_called_once()

    @patch('configurator.routes.database_routes.MongoIO')
    def test_drop_database_configurator_exception(self, mock_mongo_io_class):
        """Test DELETE /api/database when MongoIO raises ConfiguratorException."""
        # Arrange
        self._setup_config_for_local()
        mock_mongo_io = Mock()
        mock_event = ConfiguratorEvent("TEST-01", "TEST", {"error": "test"})
        mock_mongo_io.drop_database.side_effect = ConfiguratorException("Database error", mock_event)
        mock_mongo_io_class.return_value = mock_mongo_io

        # Act
        response = self.client.delete('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 500)
        # The response should contain the to_dict() structure from the exception
        self.assertIsInstance(response.json, dict)
        self.assertIn("id", response.json)
        self.assertIn("type", response.json)

    @patch('configurator.routes.database_routes.MongoIO')
    def test_drop_database_safety_limit_exceeded(self, mock_mongo_io_class):
        """Test DELETE /api/database when collections have more than 100 documents."""
        # Arrange
        self._setup_config_for_local()
        mock_mongo_io = Mock()
        mock_event = ConfiguratorEvent(
            "MON-14", 
            "DROP_DATABASE", 
            {"collections_exceeding_limit": [
                {"collection": "users", "document_count": 150},
                {"collection": "orders", "document_count": 200}
            ]}
        )
        mock_mongo_io.drop_database.side_effect = ConfiguratorException(
            "Drop database Safety Limit Exceeded - Collections with >100 documents found", 
            mock_event
        )
        mock_mongo_io_class.return_value = mock_mongo_io

        # Act
        response = self.client.delete('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertIsInstance(response.json, dict)
        self.assertIn("id", response.json)
        self.assertIn("type", response.json)

    @patch('configurator.routes.database_routes.MongoIO')
    def test_drop_database_general_exception(self, mock_mongo_io_class):
        """Test DELETE /api/database when MongoIO raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_mongo_io = Mock()
        mock_mongo_io.drop_database.side_effect = Exception("Unexpected error")
        mock_mongo_io_class.return_value = mock_mongo_io

        # Act
        response = self.client.delete('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.database_routes.MongoIO')
    def test_drop_database_connection_string_not_from_default(self, mock_mongo_io_class):
        """Test DELETE /api/database when MONGO_CONNECTION_STRING is not from default."""
        # Arrange
        self._setup_config_for_local()
        # Set MONGO_CONNECTION_STRING via environment variable (not default)
        os.environ['MONGO_CONNECTION_STRING'] = 'mongodb://custom:27017/'
        Config._instance = None
        # Recreate blueprint with new Config
        self.app = Flask(__name__)
        self.app.register_blueprint(create_database_routes(), url_prefix='/api/database')
        self.client = self.app.test_client()
        
        mock_mongo_io = Mock()
        mock_event = ConfiguratorEvent(
            "MON-12",
            "DROP_DATABASE",
            {
                "error": "Drop database not allowed when MONGO_CONNECTION_STRING is not from default",
                "source": "environment"
            }
        )
        mock_mongo_io.drop_database.side_effect = ConfiguratorException(
            "Drop database not allowed when MONGO_CONNECTION_STRING is not from default",
            mock_event
        )
        mock_mongo_io_class.return_value = mock_mongo_io

        # Act
        response = self.client.delete('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIsInstance(response_data, dict)
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        # Clean up
        if 'MONGO_CONNECTION_STRING' in os.environ:
            del os.environ['MONGO_CONNECTION_STRING']

    def test_drop_database_get_method_not_allowed(self):
        """Test that GET method is not allowed on /api/database."""
        # Act
        response = self.client.get('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_drop_database_post_method_not_allowed(self):
        """Test that POST method is not allowed on /api/database."""
        # Act
        response = self.client.post('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_drop_database_put_method_not_allowed(self):
        """Test that PUT method is not allowed on /api/database."""
        # Act
        response = self.client.put('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_drop_database_patch_method_not_allowed(self):
        """Test that PATCH method is not allowed on /api/database."""
        # Act
        response = self.client.patch('/api/database/')

        # Assert
        self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    unittest.main()