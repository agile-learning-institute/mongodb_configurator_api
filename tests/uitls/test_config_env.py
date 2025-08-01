import unittest
import os
from configurator.utils.config import Config

class TestConfigEnvironment(unittest.TestCase):
    """Test Config environment variable loading.
    NOTE: Config is never mocked in these tests. The real Config singleton is used, and config values are set/reset in setUp/tearDown.
    """

    def setUp(self):
        """Re-initialize the config for each test."""
        self.config = Config.get_instance()
        self.config.initialize()
        
        # Set all environment variables to "ENV_VALUE"
        for key, default in {**self.config.config_strings, **self.config.config_string_secrets}.items():
            if key != "BUILT_AT" and key != "INPUT_FOLDER":
                os.environ[key] = "ENV_VALUE"
            
        for key, default in self.config.config_ints.items():
            os.environ[key] = "1234"

        for key, default in self.config.config_booleans.items():
            os.environ[key] = "true"

        # Initialize the Config object
        self.config._instance = None
        self.config.initialize()
        
        # Reset environment variables 
        for key, default in {**self.config.config_strings, **self.config.config_ints, **self.config.config_string_secrets}.items():
            if key != "BUILT_AT" and key != "INPUT_FOLDER":
                del os.environ[key]
            
    def test_env_string_properties(self):
        for key, default in {**self.config.config_strings, **self.config.config_string_secrets}.items():
            if key != "BUILT_AT" and key != "INPUT_FOLDER":
                self.assertEqual(getattr(self.config, key), "ENV_VALUE")

    def test_env_int_properties(self):
        for key, default in self.config.config_ints.items():
            self.assertEqual(getattr(self.config, key), 1234)

    def test_env_boolean_properties(self):
        for key, default in self.config.config_booleans.items():
            self.assertEqual(getattr(self.config, key), True)
            
    def test_env_string_ci(self):
        for key, default in self.config.config_strings.items():
            if key != "BUILT_AT" and key != "INPUT_FOLDER":
                self._test_config_environment_value(key, "ENV_VALUE")

    def test_env_int_ci(self):
        for key, default in self.config.config_ints.items():
            self._test_config_environment_value(key, "1234")

    def test_env_secret_ci(self):
        for key, default in self.config.config_string_secrets.items():
            self._test_config_environment_value(key, "secret")

    def _test_config_environment_value(self, ci_name, value):
        """Helper function to check environment values."""
        items = self.config.config_items
        item = next((i for i in items if i['name'] == ci_name), None)
        self.assertIsNotNone(item)
        self.assertEqual(item['name'], ci_name)
        self.assertEqual(item['value'], value)
        self.assertEqual(item['from'], "environment")

if __name__ == '__main__':
    unittest.main()