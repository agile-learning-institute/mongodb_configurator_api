import os
import shutil
import tempfile
import json
import unittest
from pathlib import Path
from flask import Flask
from configurator.server import app as real_app
from configurator.utils.config import Config
from unittest.mock import patch, Mock
from configurator.routes.migration_routes import create_migration_routes
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent

class MigrationRoutesTestCase(unittest.TestCase):
    def setUp(self):
        # Store original INPUT_FOLDER if it exists
        self._original_input_folder = os.environ.get('INPUT_FOLDER')
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        
        # Create a temp directory for migrations
        self.temp_dir = tempfile.mkdtemp()
        self.migrations_dir = os.path.join(self.temp_dir, "migrations")
        os.makedirs(self.migrations_dir, exist_ok=True)
        # Create api_config directory with BUILT_AT file for local mode
        api_config_dir = os.path.join(self.temp_dir, "api_config")
        os.makedirs(api_config_dir, exist_ok=True)
        built_at_file = os.path.join(api_config_dir, "BUILT_AT")
        with open(built_at_file, "w") as f:
            f.write("Local")
        # Create MONGODB_REQUIRE_TLS file with value "false"
        require_tls_file = os.path.join(api_config_dir, "MONGODB_REQUIRE_TLS")
        with open(require_tls_file, "w") as f:
            f.write("false")
        # Set INPUT_FOLDER environment variable
        os.environ['INPUT_FOLDER'] = self.temp_dir
        
        # Modify the existing Config instance to make assert_local() pass
        # Since real_app is already initialized, we modify the existing Config instance
        config = Config.get_instance()
        # Update INPUT_FOLDER property
        config.INPUT_FOLDER = self.temp_dir
        # Ensure INPUT_FOLDER is in config_items
        input_folder_item = next((item for item in config.config_items if item['name'] == 'INPUT_FOLDER'), None)
        if input_folder_item:
            input_folder_item['value'] = self.temp_dir
            input_folder_item['from'] = 'environment'
        else:
            config.config_items.append({
                'name': 'INPUT_FOLDER',
                'value': self.temp_dir,
                'from': 'environment'
            })
        # Update BUILT_AT property and config_item to be from file with value 'Local'
        # This is what assert_local() checks
        config.BUILT_AT = 'Local'
        built_at_item = next((item for item in config.config_items if item['name'] == 'BUILT_AT'), None)
        if built_at_item:
            built_at_item['from'] = 'file'
            built_at_item['value'] = 'Local'
        else:
            config.config_items.append({
                'name': 'BUILT_AT',
                'from': 'file',
                'value': 'Local'
            })
        # Update MONGODB_REQUIRE_TLS property and config_item to be from file with value 'false'
        config.MONGODB_REQUIRE_TLS = False
        require_tls_item = next((item for item in config.config_items if item['name'] == 'MONGODB_REQUIRE_TLS'), None)
        if require_tls_item:
            require_tls_item['from'] = 'file'
            require_tls_item['value'] = 'false'
        else:
            config.config_items.append({
                'name': 'MONGODB_REQUIRE_TLS',
                'from': 'file',
                'value': 'false'
            })
        # Create some fake migration files
        self.migration1 = os.path.join(self.migrations_dir, "mig1.json")
        self.migration2 = os.path.join(self.migrations_dir, "mig2.json")
        with open(self.migration1, "w") as f:
            json.dump([{"$addFields": {"foo": "bar"}}], f)
        with open(self.migration2, "w") as f:
            json.dump([{"$unset": ["foo"]}], f)
        # Use Flask test client
        self.app = real_app.test_client()

    def tearDown(self):
        # Restore original INPUT_FOLDER
        if self._original_input_folder:
            os.environ['INPUT_FOLDER'] = self._original_input_folder
        elif 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        # Restore Config to default state
        config = Config.get_instance()
        # Restore INPUT_FOLDER
        config.INPUT_FOLDER = os.getenv("INPUT_FOLDER", "/input")
        input_folder_item = next((item for item in config.config_items if item['name'] == 'INPUT_FOLDER'), None)
        if input_folder_item:
            input_folder_item['value'] = config.INPUT_FOLDER
            input_folder_item['from'] = 'default' if not os.getenv("INPUT_FOLDER") else 'environment'
        # Restore BUILT_AT to default
        config.BUILT_AT = 'DEFAULT! Set in code'
        built_at_item = next((item for item in config.config_items if item['name'] == 'BUILT_AT'), None)
        if built_at_item:
            built_at_item['from'] = 'default'
            built_at_item['value'] = 'DEFAULT! Set in code'
        # Clean up temp directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_list_migrations(self):
        """Test GET /api/migrations/ endpoint."""
        resp = self.app.get("/api/migrations/")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        # For successful responses, expect File objects with metadata
        self.assertIsInstance(data, list)
        self.assertTrue(any("mig1.json" in file.get("file_name", "") for file in data))
        self.assertTrue(any("mig2.json" in file.get("file_name", "") for file in data))
        # Check that each item has the expected File object structure
        for file in data:
            self.assertIn("file_name", file)
            self.assertIn("created_at", file)
            self.assertIn("updated_at", file)
            self.assertIn("size", file)

    def test_get_migration(self):
        resp = self.app.get("/api/migrations/mig1.json/")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        # For successful responses, expect data directly, not wrapped in event envelope
        self.assertIsInstance(data, list)
        self.assertEqual(data, [{"$addFields": {"foo": "bar"}}])

    def test_get_migration_not_found(self):
        resp = self.app.get("/api/migrations/doesnotexist.json/")
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertIn("id", data)
        self.assertIn("type", data)
        self.assertIn("status", data)
        self.assertIn("data", data)
        self.assertEqual(data["status"], "FAILURE")

    def test_put_migration(self):
        """Test PUT /api/migrations/<file_name>/."""
        # Arrange - Config is already set up for local mode in setUp
        # Ensure Config is still in local mode (in case another test modified it)
        config = Config.get_instance()
        built_at_item = next((item for item in config.config_items if item['name'] == 'BUILT_AT'), None)
        if not built_at_item or built_at_item.get('from') != 'file' or built_at_item.get('value') != 'Local':
            # Re-setup Config for local mode
            config.BUILT_AT = 'Local'
            if built_at_item:
                built_at_item['from'] = 'file'
                built_at_item['value'] = 'Local'
            else:
                config.config_items.append({
                    'name': 'BUILT_AT',
                    'from': 'file',
                    'value': 'Local'
                })
        # Also ensure MONGODB_REQUIRE_TLS is set to false
        require_tls_item = next((item for item in config.config_items if item['name'] == 'MONGODB_REQUIRE_TLS'), None)
        if require_tls_item:
            require_tls_item['from'] = 'file'
            require_tls_item['value'] = 'false'
        else:
            config.config_items.append({
                'name': 'MONGODB_REQUIRE_TLS',
                'from': 'file',
                'value': 'false'
            })
        config.MONGODB_REQUIRE_TLS = False
        test_data = {"migration": "test data"}
        
        # Act
        response = self.app.put('/api/migrations/mig1.json/', json=test_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, test_data)

    def test_delete_migration(self):
        # Arrange - Config is already set up for local mode in setUp
        # Ensure Config is still in local mode (in case another test modified it)
        config = Config.get_instance()
        built_at_item = next((item for item in config.config_items if item['name'] == 'BUILT_AT'), None)
        if not built_at_item or built_at_item.get('from') != 'file' or built_at_item.get('value') != 'Local':
            # Re-setup Config for local mode
            config.BUILT_AT = 'Local'
            if built_at_item:
                built_at_item['from'] = 'file'
                built_at_item['value'] = 'Local'
            else:
                config.config_items.append({
                    'name': 'BUILT_AT',
                    'from': 'file',
                    'value': 'Local'
                })
        # Also ensure MONGODB_REQUIRE_TLS is set to false
        require_tls_item = next((item for item in config.config_items if item['name'] == 'MONGODB_REQUIRE_TLS'), None)
        if require_tls_item:
            require_tls_item['from'] = 'file'
            require_tls_item['value'] = 'false'
        else:
            config.config_items.append({
                'name': 'MONGODB_REQUIRE_TLS',
                'from': 'file',
                'value': 'false'
            })
        config.MONGODB_REQUIRE_TLS = False
        resp = self.app.delete("/api/migrations/mig1.json/")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        # For successful responses, expect ConfiguratorEvent object
        self.assertIn("id", data)
        self.assertIn("type", data)
        self.assertIn("status", data)
        self.assertIn("data", data)
        self.assertEqual(data["status"], "SUCCESS")

    def test_delete_migration_not_found(self):
        resp = self.app.delete("/api/migrations/doesnotexist.json/")
        self.assertEqual(resp.status_code, 500)  # Should return event with FAILURE status
        data = resp.get_json()
        self.assertIn("id", data)
        self.assertIn("type", data)
        self.assertIn("status", data)
        self.assertIn("data", data)
        self.assertEqual(data["status"], "FAILURE")

class TestMigrationRoutes(unittest.TestCase):
    """Test cases for migration routes."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear Config singleton to ensure clean state
        Config._instance = None
        # Store original INPUT_FOLDER if it exists
        self._original_input_folder = os.environ.get('INPUT_FOLDER')
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        
        self.app = Flask(__name__)
        self.app.register_blueprint(create_migration_routes(), url_prefix='/api/migrations')
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
        self.app.register_blueprint(create_migration_routes(), url_prefix='/api/migrations')
        self.client = self.app.test_client()

    @patch('configurator.routes.migration_routes.FileIO')
    def test_list_migrations_success(self, mock_file_io):
        """Test successful GET /api/migrations/."""
        # Arrange
        mock_file1 = Mock()
        mock_file1.to_dict.return_value = {"file_name": "migration1.json", "size": 100, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}
        mock_file2 = Mock()
        mock_file2.to_dict.return_value = {"file_name": "migration2.json", "size": 200, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}
        mock_files = [mock_file1, mock_file2]
        
        with patch('configurator.routes.migration_routes.FileIO') as mock_file_io:
            mock_file_io.get_documents.return_value = mock_files
            
            # Act
            response = self.client.get('/api/migrations/')
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = response.json
            self.assertEqual(response_data, [{"file_name": "migration1.json", "size": 100, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}, {"file_name": "migration2.json", "size": 200, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}])

    @patch('configurator.routes.migration_routes.FileIO')
    def test_list_migrations_general_exception(self, mock_file_io):
        """Test GET /api/migrations/ when FileIO raises a general exception."""
        # Arrange
        mock_file_io.get_documents.side_effect = Exception("Unexpected error")

        # Act
        response = self.client.get('/api/migrations/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.migration_routes.FileIO')
    def test_get_migration_success(self, mock_file_io):
        """Test successful GET /api/migrations/<file_name>."""
        # Arrange
        mock_file_io.get_document.return_value = {"name": "test_migration", "operations": []}

        # Act
        response = self.client.get('/api/migrations/test_migration.json/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertEqual(response_data, {"name": "test_migration", "operations": []})

    @patch('configurator.routes.migration_routes.FileIO')
    def test_get_migration_general_exception(self, mock_file_io):
        """Test GET /api/migrations/<file_name> when FileIO raises a general exception."""
        # Arrange
        mock_file_io.get_document.side_effect = Exception("Unexpected error")

        # Act
        response = self.client.get('/api/migrations/test_migration.json/')

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.migration_routes.FileIO')
    def test_put_migration_success(self, mock_file_io):
        """Test successful PUT /api/migrations/<file_name>."""
        # Arrange
        self._setup_config_for_local()
        test_data = {"name": "test_migration", "operations": []}
        mock_file_io.put_document.return_value = test_data

        # Act
        response = self.client.put('/api/migrations/test_migration.json/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data, test_data)

    @patch('configurator.routes.migration_routes.FileIO')
    def test_put_migration_general_exception(self, mock_file_io):
        """Test PUT /api/migrations/<file_name> when FileIO raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_file_io.put_document.side_effect = Exception("Unexpected error")
        test_data = {"name": "test_migration", "operations": []}

        # Act
        response = self.client.put('/api/migrations/test_migration.json/', json=test_data)

        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    @patch('configurator.routes.migration_routes.os.path.exists')
    @patch('configurator.routes.migration_routes.FileIO')
    def test_delete_migration_success(self, mock_file_io, mock_exists):
        """Test successful DELETE /api/migrations/<file_name>."""
        # Arrange
        self._setup_config_for_local()
        mock_exists.return_value = True
        mock_event = Mock()
        mock_event.status = "SUCCESS"
        mock_event.to_dict.return_value = {"id": "MIG-06", "type": "DELETE_MIGRATION", "status": "SUCCESS", "data": "test_migration.json deleted"}
        mock_file_io.delete_document.return_value = mock_event

        # Act
        response = self.client.delete('/api/migrations/test_migration.json/')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "SUCCESS")

    @patch('configurator.routes.migration_routes.FileIO')
    def test_delete_migration_general_exception(self, mock_file_io):
        """Test DELETE /api/migrations/<file_name> when FileIO raises a general exception."""
        # Arrange
        self._setup_config_for_local()
        mock_event = Mock()
        mock_event.status = "FAILURE"
        mock_event.to_dict.return_value = {"id": "MIG-06", "type": "DELETE_MIGRATION", "status": "FAILURE", "data": "Unexpected error"}
        mock_file_io.delete_document.return_value = mock_event

        # Act
        response = self.client.delete('/api/migrations/test_migration.json/')

        # Assert
        self.assertEqual(response.status_code, 200)  # Should return event with FAILURE status
        response_data = response.json
        self.assertIn("id", response_data)
        self.assertIn("type", response_data)
        self.assertIn("status", response_data)
        self.assertIn("data", response_data)
        self.assertEqual(response_data["status"], "FAILURE")

    def test_migrations_post_method_not_allowed(self):
        """Test that POST method is not allowed."""
        response = self.client.post('/api/migrations/')
        self.assertEqual(response.status_code, 405)

    def test_migrations_patch_method_not_allowed(self):
        """Test that PATCH method is not allowed for individual migrations."""
        response = self.client.patch('/api/migrations/test_migration.json/')
        self.assertEqual(response.status_code, 405)

    def test_get_migrations_success(self):
        """Test successful GET /api/migrations/."""
        # Arrange
        mock_file1 = Mock()
        mock_file1.file_name = "migration1.json"
        mock_file1.to_dict.return_value = {"file_name": "migration1.json", "size": 100, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}
        mock_file2 = Mock()
        mock_file2.file_name = "migration2.json"
        mock_file2.to_dict.return_value = {"file_name": "migration2.json", "size": 200, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}
        mock_files = [mock_file1, mock_file2]
        
        with patch('configurator.routes.migration_routes.FileIO') as mock_file_io:
            mock_file_io.get_documents.return_value = mock_files
            
            # Act
            response = self.client.get('/api/migrations/')
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = response.json
            self.assertIsInstance(response_data, list)
            self.assertEqual(len(response_data), 2)
            self.assertIn("file_name", response_data[0])
            self.assertIn("file_name", response_data[1])
            self.assertEqual(response_data[0]["file_name"], "migration1.json")
            self.assertEqual(response_data[1]["file_name"], "migration2.json")

if __name__ == "__main__":
    unittest.main() 