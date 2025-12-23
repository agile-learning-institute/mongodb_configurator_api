import unittest
import os
import tempfile
from pathlib import Path
from configurator.utils.config import Config
from configurator.utils.configurator_exception import ConfiguratorForbiddenException

class TestAssertLocal(unittest.TestCase):
    """Test cases for Config.assert_local() method."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear the singleton instance to ensure clean state
        Config._instance = None

    def tearDown(self):
        """Clean up after tests."""
        # Clear the singleton instance
        Config._instance = None
        # Clean up any environment variables we set
        if 'BUILT_AT' in os.environ:
            del os.environ['BUILT_AT']
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']

    def test_assert_local_succeeds_when_file_and_local(self):
        """Test that assert_local() succeeds (no exception) when BUILT_AT is from file and value is 'Local'."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create api_config directory
            api_config_dir = Path(temp_dir) / "api_config"
            api_config_dir.mkdir()
            
            # Create BUILT_AT file with value "Local"
            built_at_file = api_config_dir / "BUILT_AT"
            built_at_file.write_text("Local")
            
            # Create MONGODB_REQUIRE_TLS file with value "false"
            require_tls_file = api_config_dir / "MONGODB_REQUIRE_TLS"
            require_tls_file.write_text("false")
            
            # Set INPUT_FOLDER environment variable
            os.environ['INPUT_FOLDER'] = temp_dir
            
            # Get config instance
            config = Config.get_instance()
            
            # Assert - should not raise exception
            try:
                config.assert_local()
            except ConfiguratorForbiddenException:
                self.fail("assert_local() raised ConfiguratorForbiddenException unexpectedly!")

    def test_assert_local_raises_when_file_and_not_local(self):
        """Test that assert_local() raises ConfiguratorForbiddenException when BUILT_AT is from file but value is not 'Local'."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create api_config directory
            api_config_dir = Path(temp_dir) / "api_config"
            api_config_dir.mkdir()
            
            # Create BUILT_AT file with value "Production"
            built_at_file = api_config_dir / "BUILT_AT"
            built_at_file.write_text("Production")
            
            # Set INPUT_FOLDER environment variable
            os.environ['INPUT_FOLDER'] = temp_dir
            
            # Get config instance
            config = Config.get_instance()
            
            # Assert - should raise ConfiguratorForbiddenException
            with self.assertRaises(ConfiguratorForbiddenException) as context:
                config.assert_local()
            
            self.assertIn("Write operations are only allowed", str(context.exception))
            self.assertIsNotNone(context.exception.event)
            self.assertEqual(context.exception.event.status, "FAILURE")

    def test_assert_local_raises_when_from_environment(self):
        """Test that assert_local() raises ConfiguratorForbiddenException when BUILT_AT is from environment variable."""
        # Set BUILT_AT environment variable
        os.environ['BUILT_AT'] = 'Local'
        
        # Get config instance
        config = Config.get_instance()
        
        # Assert - should raise ConfiguratorForbiddenException
        with self.assertRaises(ConfiguratorForbiddenException) as context:
            config.assert_local()
        
        self.assertIn("Write operations are only allowed", str(context.exception))
        self.assertIsNotNone(context.exception.event)
        self.assertEqual(context.exception.event.status, "FAILURE")

    def test_assert_local_raises_when_from_default(self):
        """Test that assert_local() raises ConfiguratorForbiddenException when BUILT_AT is from default."""
        # Get config instance (no file, no environment variable)
        config = Config.get_instance()
        
        # Assert - should raise ConfiguratorForbiddenException
        with self.assertRaises(ConfiguratorForbiddenException) as context:
            config.assert_local()
        
        self.assertIn("Write operations are only allowed", str(context.exception))
        self.assertIsNotNone(context.exception.event)
        self.assertEqual(context.exception.event.status, "FAILURE")

    def test_assert_local_raises_when_built_at_missing(self):
        """Test that assert_local() raises ConfiguratorForbiddenException when BUILT_AT config_item is missing."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set INPUT_FOLDER environment variable
            os.environ['INPUT_FOLDER'] = temp_dir
            
            # Get config instance
            config = Config.get_instance()
            
            # Manually remove BUILT_AT from config_items
            config.config_items = [item for item in config.config_items if item['name'] != 'BUILT_AT']
            
            # Assert - should raise ConfiguratorForbiddenException
            with self.assertRaises(ConfiguratorForbiddenException) as context:
                config.assert_local()
            
            self.assertIn("Write operations are only allowed", str(context.exception))
            self.assertIsNotNone(context.exception.event)
            self.assertEqual(context.exception.event.status, "FAILURE")
            self.assertIn("BUILT_AT configuration item not found", str(context.exception.event.data))

    def test_assert_local_raises_when_require_tls_true(self):
        """Test that assert_local() raises ConfiguratorForbiddenException when MONGODB_REQUIRE_TLS is True."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create api_config directory
            api_config_dir = Path(temp_dir) / "api_config"
            api_config_dir.mkdir()
            
            # Create BUILT_AT file with value "Local"
            built_at_file = api_config_dir / "BUILT_AT"
            built_at_file.write_text("Local")
            
            # Create MONGODB_REQUIRE_TLS file with value "true"
            require_tls_file = api_config_dir / "MONGODB_REQUIRE_TLS"
            require_tls_file.write_text("true")
            
            # Set INPUT_FOLDER environment variable
            os.environ['INPUT_FOLDER'] = temp_dir
            
            # Get config instance
            config = Config.get_instance()
            
            # Assert - should raise ConfiguratorForbiddenException
            with self.assertRaises(ConfiguratorForbiddenException) as context:
                config.assert_local()
            
            self.assertIn("Write operations are only allowed", str(context.exception))
            self.assertIn("MONGODB_REQUIRE_TLS", str(context.exception))
            self.assertIsNotNone(context.exception.event)
            self.assertEqual(context.exception.event.status, "FAILURE")
            self.assertEqual(context.exception.event.id, "CFG-ASSERT-04")

    def test_assert_local_raises_when_require_tls_missing(self):
        """Test that assert_local() raises ConfiguratorForbiddenException when MONGODB_REQUIRE_TLS config_item is missing."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create api_config directory
            api_config_dir = Path(temp_dir) / "api_config"
            api_config_dir.mkdir()
            
            # Create BUILT_AT file with value "Local"
            built_at_file = api_config_dir / "BUILT_AT"
            built_at_file.write_text("Local")
            
            # Set INPUT_FOLDER environment variable
            os.environ['INPUT_FOLDER'] = temp_dir
            
            # Get config instance
            config = Config.get_instance()
            
            # Manually remove MONGODB_REQUIRE_TLS from config_items
            config.config_items = [item for item in config.config_items if item['name'] != 'MONGODB_REQUIRE_TLS']
            
            # Assert - should raise ConfiguratorForbiddenException
            with self.assertRaises(ConfiguratorForbiddenException) as context:
                config.assert_local()
            
            self.assertIn("Write operations are only allowed", str(context.exception))
            self.assertIn("MONGODB_REQUIRE_TLS", str(context.exception))
            self.assertIsNotNone(context.exception.event)
            self.assertEqual(context.exception.event.status, "FAILURE")
            self.assertEqual(context.exception.event.id, "CFG-ASSERT-03")

if __name__ == '__main__':
    unittest.main()

