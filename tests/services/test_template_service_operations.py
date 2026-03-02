import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from configurator.services.template_service import TemplateService
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.utils.config import Config


class TestTemplateService(unittest.TestCase):
    """Focused unit tests for TemplateService class"""

    def setUp(self):
        """Set up test environment"""
        Config._instance = None
        self.test_collection_name = "test_collection"
        self._original_input_folder = os.environ.get('INPUT_FOLDER')

    def tearDown(self):
        """Clean up after tests."""
        Config._instance = None
        if self._original_input_folder:
            os.environ['INPUT_FOLDER'] = self._original_input_folder
        elif 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']

    def _setup_temp_input_folder(self):
        """Create temp directory with api_config for local mode."""
        self.temp_dir = tempfile.mkdtemp()
        api_config = Path(self.temp_dir) / "api_config"
        api_config.mkdir()
        (api_config / "BUILT_AT").write_text("Local")
        (api_config / "MONGODB_REQUIRE_TLS").write_text("false")
        for folder in ["configurations", "dictionaries", "test_data"]:
            (Path(self.temp_dir) / folder).mkdir()
        os.environ['INPUT_FOLDER'] = self.temp_dir
        Config._instance = None
        return self.temp_dir

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.template_service.FileIO')
    def test_create_collection_creates_config_dictionary_test_data(self, mock_file_io, mock_file_io_base):
        """Test create_collection creates config, dictionary, and test_data files."""
        mock_file_io.file_exists.return_value = False
        mock_file_io.put_document.return_value = {}
        mock_file_io_base.put_document.return_value = {}

        self._setup_temp_input_folder()

        result = TemplateService.create_collection(self.test_collection_name)

        self.assertEqual(result["configuration_file"], "test_collection.yaml")
        self.assertEqual(result["dictionary_file"], "test_collection.1.0.0.yaml")
        self.assertEqual(result["test_data_file"], "test_collection.1.0.0.0.json")
        self.assertEqual(result["version"], "1.0.0.0")

        # Should have saved config (via Configuration.save), dictionary (via Dictionary.save), and test_data
        total_put_calls = mock_file_io.put_document.call_count + mock_file_io_base.put_document.call_count
        self.assertGreaterEqual(total_put_calls, 3)

    def test_create_collection_raises_when_config_exists(self):
        """Test create_collection raises when configuration already exists."""
        with patch('configurator.services.template_service.FileIO') as mock_file_io:
            mock_file_io.file_exists.side_effect = lambda folder, name: (
                name == "test_collection.yaml" if folder == "configurations" else False
            )

            self._setup_temp_input_folder()

            with self.assertRaises(ConfiguratorException) as ctx:
                TemplateService.create_collection(self.test_collection_name)
            self.assertIn("already exists", str(ctx.exception))

    def test_create_collection_raises_when_dictionary_exists(self):
        """Test create_collection raises when dictionary already exists."""
        with patch('configurator.services.template_service.FileIO') as mock_file_io:
            def file_exists(folder, name):
                if folder == "configurations":
                    return name == "test_collection.yaml"
                if folder == "dictionaries":
                    return name == "test_collection.1.0.0.yaml"
                return False
            mock_file_io.file_exists.side_effect = file_exists

            self._setup_temp_input_folder()

            with self.assertRaises(ConfiguratorException) as ctx:
                TemplateService.create_collection(self.test_collection_name)
            self.assertIn("already exists", str(ctx.exception))

    @patch('configurator.services.service_base.FileIO')
    @patch('configurator.services.template_service.FileIO')
    def test_create_collection_with_description(self, mock_file_io, mock_file_io_base):
        """Test create_collection accepts optional description."""
        mock_file_io.file_exists.return_value = False
        mock_file_io.put_document.return_value = {}
        mock_file_io_base.put_document.return_value = {}

        self._setup_temp_input_folder()

        result = TemplateService.create_collection(
            self.test_collection_name,
            description="My custom description"
        )
        self.assertEqual(result["version"], "1.0.0.0")
        self.assertEqual(result["dictionary_file"], "test_collection.1.0.0.yaml")

    def test_load_dictionary_template_substitutes_placeholders(self):
        """Test that template placeholders are substituted."""
        from configurator.services.template_service import _load_dictionary_template
        result = _load_dictionary_template("my_collection", "Custom description")
        self.assertIn("name", result)
        self.assertEqual(result.get("description"), "Custom description")
        self.assertEqual(result.get("type"), "void")


if __name__ == '__main__':
    unittest.main()
