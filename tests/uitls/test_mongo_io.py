"""
Unit tests for MongoIO class, specifically testing drop_database method safety checks.
"""
import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from configurator.utils.config import Config
from configurator.utils.mongo_io import MongoIO
from configurator.utils.configurator_exception import ConfiguratorException


class TestMongoIODropDatabase(unittest.TestCase):
    """Unit tests for MongoIO.drop_database method safety checks."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear Config singleton to ensure clean state
        Config._instance = None
        # Store original environment variables
        self._original_input_folder = os.environ.get('INPUT_FOLDER')
        self._original_mongo_connection_string = os.environ.get('MONGO_CONNECTION_STRING')
        self._original_enable_drop_database = os.environ.get('ENABLE_DROP_DATABASE')
        self._original_built_at = os.environ.get('BUILT_AT')
        
        # Clean up environment
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        if 'MONGO_CONNECTION_STRING' in os.environ:
            del os.environ['MONGO_CONNECTION_STRING']
        if 'ENABLE_DROP_DATABASE' in os.environ:
            del os.environ['ENABLE_DROP_DATABASE']
        if 'BUILT_AT' in os.environ:
            del os.environ['BUILT_AT']
        
        self.temp_dir = None

    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment variables
        if self._original_input_folder:
            os.environ['INPUT_FOLDER'] = self._original_input_folder
        elif 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
            
        if self._original_mongo_connection_string:
            os.environ['MONGO_CONNECTION_STRING'] = self._original_mongo_connection_string
        elif 'MONGO_CONNECTION_STRING' in os.environ:
            del os.environ['MONGO_CONNECTION_STRING']
            
        if self._original_enable_drop_database:
            os.environ['ENABLE_DROP_DATABASE'] = self._original_enable_drop_database
        elif 'ENABLE_DROP_DATABASE' in os.environ:
            del os.environ['ENABLE_DROP_DATABASE']
            
        if self._original_built_at:
            os.environ['BUILT_AT'] = self._original_built_at
        elif 'BUILT_AT' in os.environ:
            del os.environ['BUILT_AT']
        
        # Clear Config singleton
        Config._instance = None
        
        # Clean up temp directory if created
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def _setup_config_for_drop_database(self, mongo_connection_string_from='default'):
        """Set up Config for drop_database testing.
        
        Args:
            mongo_connection_string_from: 'default', 'environment', or 'file' to control
                where MONGO_CONNECTION_STRING comes from
        """
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        api_config_dir = Path(self.temp_dir) / "api_config"
        api_config_dir.mkdir()
        
        # Create BUILT_AT file with value "Local"
        built_at_file = api_config_dir / "BUILT_AT"
        built_at_file.write_text("Local")
        
        # Create ENABLE_DROP_DATABASE file
        enable_drop_file = api_config_dir / "ENABLE_DROP_DATABASE"
        enable_drop_file.write_text("true")
        
        # Create MONGODB_REQUIRE_TLS file (set to false for local dev tests)
        mongodb_require_tls_file = api_config_dir / "MONGODB_REQUIRE_TLS"
        mongodb_require_tls_file.write_text("false")
        
        # Set MONGO_CONNECTION_STRING based on the parameter
        if mongo_connection_string_from == 'environment':
            os.environ['MONGO_CONNECTION_STRING'] = 'mongodb://custom:27017/'
        elif mongo_connection_string_from == 'file':
            mongo_conn_file = api_config_dir / "MONGO_CONNECTION_STRING"
            mongo_conn_file.write_text("mongodb://file-based:27017/")
        # If 'default', don't set it anywhere (will use default value)
        
        # Set INPUT_FOLDER environment variable
        os.environ['INPUT_FOLDER'] = self.temp_dir
        
        # Clear and reinitialize Config
        Config._instance = None
        config = Config.get_instance()
        return config

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_drop_database_connection_string_from_default_success(self, mock_mongo_client):
        """Test drop_database succeeds when MONGO_CONNECTION_STRING is from default."""
        # Arrange
        config = self._setup_config_for_drop_database(mongo_connection_string_from='default')
        
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.name = "test_db"
        mock_db.list_collection_names.return_value = []
        mock_client.get_database.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        mongo_io = MongoIO(config.MONGO_CONNECTION_STRING, config.MONGO_DB_NAME)
        mongo_io.db = mock_db
        mongo_io.client = mock_client
        
        # Act
        event = mongo_io.drop_database()
        
        # Assert
        self.assertEqual(event.status, "SUCCESS")
        mock_client.drop_database.assert_called_once_with("test_db")

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_drop_database_connection_string_from_environment_fails(self, mock_mongo_client):
        """Test drop_database fails when MONGO_CONNECTION_STRING is from environment."""
        # Arrange
        config = self._setup_config_for_drop_database(mongo_connection_string_from='environment')
        
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.name = "test_db"
        mock_client.get_database.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        mongo_io = MongoIO(config.MONGO_CONNECTION_STRING, config.MONGO_DB_NAME)
        mongo_io.db = mock_db
        mongo_io.client = mock_client
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            mongo_io.drop_database()
        
        exception = context.exception
        self.assertIn("not from default", str(exception))
        self.assertEqual(exception.event.id, "MON-12")
        self.assertEqual(exception.event.status, "FAILURE")
        self.assertEqual(exception.event.data.get("source"), "environment")
        # Verify drop_database was not called
        mock_client.drop_database.assert_not_called()

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_drop_database_connection_string_from_file_fails(self, mock_mongo_client):
        """Test drop_database fails when MONGO_CONNECTION_STRING is from file."""
        # Arrange
        config = self._setup_config_for_drop_database(mongo_connection_string_from='file')
        
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.name = "test_db"
        mock_client.get_database.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        mongo_io = MongoIO(config.MONGO_CONNECTION_STRING, config.MONGO_DB_NAME)
        mongo_io.db = mock_db
        mongo_io.client = mock_client
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            mongo_io.drop_database()
        
        exception = context.exception
        self.assertIn("not from default", str(exception))
        self.assertEqual(exception.event.id, "MON-12")
        self.assertEqual(exception.event.status, "FAILURE")
        self.assertEqual(exception.event.data.get("source"), "file")
        # Verify drop_database was not called
        mock_client.drop_database.assert_not_called()

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_drop_database_connection_string_missing_fails(self, mock_mongo_client):
        """Test drop_database fails when MONGO_CONNECTION_STRING config item is missing."""
        # Arrange
        config = self._setup_config_for_drop_database(mongo_connection_string_from='default')
        
        # Remove MONGO_CONNECTION_STRING from config_items (simulating missing item)
        config.config_items = [item for item in config.config_items 
                               if item['name'] != 'MONGO_CONNECTION_STRING']
        
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.name = "test_db"
        mock_client.get_database.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        mongo_io = MongoIO(config.MONGO_CONNECTION_STRING, config.MONGO_DB_NAME)
        mongo_io.db = mock_db
        mongo_io.client = mock_client
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            mongo_io.drop_database()
        
        exception = context.exception
        self.assertIn("not found", str(exception))
        self.assertEqual(exception.event.id, "MON-12")
        self.assertEqual(exception.event.status, "FAILURE")
        # Verify drop_database was not called
        mock_client.drop_database.assert_not_called()

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_tls_validation_requires_tls_with_mongodb_srv_succeeds(self, mock_mongo_client):
        """Test that connection succeeds when MONGODB_REQUIRE_TLS is True and connection string uses mongodb+srv://"""
        # Arrange
        Config._instance = None
        os.environ['MONGODB_REQUIRE_TLS'] = 'true'
        config = Config.get_instance()
        
        # Mock MongoDB client
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.name = "test_db"
        mock_client.get_database.return_value = mock_db
        mock_client.admin.command.return_value = {"ok": 1}
        mock_mongo_client.return_value = mock_client
        
        # Act
        mongo_io = MongoIO("mongodb+srv://user:pass@cluster.mongodb.net/", "test_db")
        
        # Assert
        self.assertIsNotNone(mongo_io.client)
        self.assertIsNotNone(mongo_io.db)
        mock_mongo_client.assert_called_once()
        del os.environ['MONGODB_REQUIRE_TLS']
        Config._instance = None

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_tls_validation_requires_tls_with_mongodb_fails(self, mock_mongo_client):
        """Test that connection fails when MONGODB_REQUIRE_TLS is True but connection string uses mongodb://"""
        # Arrange
        Config._instance = None
        os.environ['MONGODB_REQUIRE_TLS'] = 'true'
        config = Config.get_instance()
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            MongoIO("mongodb://localhost:27017/", "test_db")
        
        exception = context.exception
        self.assertIn("MONGODB_REQUIRE_TLS is True", str(exception))
        self.assertEqual(exception.event.id, "MON-02")
        self.assertEqual(exception.event.status, "FAILURE")
        self.assertEqual(exception.event.type, "TLS_VALIDATION")
        # Verify MongoClient was not called
        mock_mongo_client.assert_not_called()
        del os.environ['MONGODB_REQUIRE_TLS']
        Config._instance = None

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_tls_validation_no_tls_required_with_mongodb_succeeds(self, mock_mongo_client):
        """Test that connection succeeds when MONGODB_REQUIRE_TLS is False and connection string uses mongodb://"""
        # Arrange
        Config._instance = None
        os.environ['MONGODB_REQUIRE_TLS'] = 'false'
        config = Config.get_instance()
        
        # Mock MongoDB client
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.name = "test_db"
        mock_client.get_database.return_value = mock_db
        mock_client.admin.command.return_value = {"ok": 1}
        mock_mongo_client.return_value = mock_client
        
        # Act
        mongo_io = MongoIO("mongodb://localhost:27017/", "test_db")
        
        # Assert
        self.assertIsNotNone(mongo_io.client)
        self.assertIsNotNone(mongo_io.db)
        mock_mongo_client.assert_called_once()
        del os.environ['MONGODB_REQUIRE_TLS']
        Config._instance = None

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_tls_validation_no_tls_required_with_mongodb_srv_fails(self, mock_mongo_client):
        """Test that connection fails when MONGODB_REQUIRE_TLS is False but connection string uses mongodb+srv://"""
        # Arrange
        Config._instance = None
        os.environ['MONGODB_REQUIRE_TLS'] = 'false'
        config = Config.get_instance()
        
        # Act & Assert
        with self.assertRaises(ConfiguratorException) as context:
            MongoIO("mongodb+srv://user:pass@cluster.mongodb.net/", "test_db")
        
        exception = context.exception
        self.assertIn("MONGODB_REQUIRE_TLS is False", str(exception))
        self.assertEqual(exception.event.id, "MON-02")
        self.assertEqual(exception.event.status, "FAILURE")
        self.assertEqual(exception.event.type, "TLS_VALIDATION")
        # Verify MongoClient was not called
        mock_mongo_client.assert_not_called()
        del os.environ['MONGODB_REQUIRE_TLS']
        Config._instance = None

    @patch('configurator.utils.mongo_io.MongoClient')
    def test_tls_validation_default_true_with_mongodb_srv_succeeds(self, mock_mongo_client):
        """Test that connection succeeds with default MONGODB_REQUIRE_TLS=True when using mongodb+srv://"""
        # Arrange
        Config._instance = None
        # Don't set MONGODB_REQUIRE_TLS, should default to True
        config = Config.get_instance()
        
        # Mock MongoDB client
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.name = "test_db"
        mock_client.get_database.return_value = mock_db
        mock_client.admin.command.return_value = {"ok": 1}
        mock_mongo_client.return_value = mock_client
        
        # Act
        mongo_io = MongoIO("mongodb+srv://user:pass@cluster.mongodb.net/", "test_db")
        
        # Assert
        self.assertIsNotNone(mongo_io.client)
        self.assertIsNotNone(mongo_io.db)
        mock_mongo_client.assert_called_once()
        Config._instance = None


if __name__ == '__main__':
    unittest.main()

