import os
import json
from pathlib import Path
from configurator.utils.configurator_exception import ConfiguratorForbiddenException, ConfiguratorEvent

import logging
logger = logging.getLogger(__name__)

class Config:
    _instance = None  # Singleton instance

    def __init__(self):
        if Config._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Config._instance = self
            self.config_items = []

            # Set INPUT_FOLDER from environment or default FIRST
            self.INPUT_FOLDER = os.getenv("INPUT_FOLDER", "/input")

            # Declare instance variables to support IDE code assist
            self.BUILT_AT = ''
            self.API_BUILT_AT = ''
            self.LOGGING_LEVEL = ''
            self.MONGO_DB_NAME = ''
            self.MONGO_CONNECTION_STRING = ''
            self.ENUMERATORS_COLLECTION_NAME = ''
            self.VERSION_COLLECTION_NAME = ''
            self.TYPE_FOLDER = ''
            self.DICTIONARY_FOLDER = ''
            self.CONFIGURATION_FOLDER = ''
            self.TEST_DATA_FOLDER = ''
            self.MIGRATIONS_FOLDER = ''
            self.API_CONFIG_FOLDER = ''
            self.ENUMERATOR_FOLDER = ''
            self.API_PORT = 0
            self.SPA_PORT = 0
            self.AUTO_PROCESS = False
            self.EXIT_AFTER_PROCESSING = False
            self.LOAD_TEST_DATA = False
            self.ENABLE_DROP_DATABASE = False
            self.MONGODB_REQUIRE_TLS = False
            self.RENDER_STACK_MAX_DEPTH = 0
            self.UI_HEADER = ''
    
            # Default Values grouped by value type            
            self.config_strings = {
                "BUILT_AT": "DEFAULT! Set in code",
                "INPUT_FOLDER": "/input",
                "LOGGING_LEVEL": "INFO", 
                "MONGO_DB_NAME": "configurator",
                "VERSION_COLLECTION_NAME": "CollectionVersions",
                "ENUMERATORS_COLLECTION_NAME": "DatabaseEnumerators",
                "TYPE_FOLDER": "types",
                "DICTIONARY_FOLDER": "dictionaries",
                "CONFIGURATION_FOLDER": "configurations",
                "TEST_DATA_FOLDER": "test_data",
                "MIGRATIONS_FOLDER": "migrations",
                "API_CONFIG_FOLDER": "api_config",
                "ENUMERATOR_FOLDER": "enumerators",
                "UI_HEADER": "MongoDB Configurator",
            }
            self.config_ints = {
                "API_PORT": "8081",
                "SPA_PORT": "8082",
                "RENDER_STACK_MAX_DEPTH": "100",
            }
            self.config_booleans = {
                "AUTO_PROCESS": "false",
                "EXIT_AFTER_PROCESSING": "false",
                "LOAD_TEST_DATA": "false",
                "ENABLE_DROP_DATABASE": "false",
                "MONGODB_REQUIRE_TLS": "true",
            }            
            self.config_string_secrets = {  
                "MONGO_CONNECTION_STRING": "mongodb://mongodb:27017/"
            }

            # Initialize configuration
            self.initialize()
            self.configure_logging()

    def initialize(self):
        """Initialize configuration values."""
        self.config_items = []

        # Add INPUT_FOLDER to config_items since it's already set
        self.config_items.append({
            "name": "INPUT_FOLDER",
            "value": self.INPUT_FOLDER,
            "from": "default" if not os.getenv("INPUT_FOLDER") else "environment"
        })

        # Initialize API_BUILT_AT from configurator directory
        self._initialize_api_built_at()

        # Initialize Config Strings (except INPUT_FOLDER)
        for key, default in self.config_strings.items():
            if key == "INPUT_FOLDER":
                continue  # Already set
            value = self._get_config_value(key, default, False)
            setattr(self, key, value)
        
        # Initialize Config Integers
        for key, default in self.config_ints.items():
            value = int(self._get_config_value(key, default, False))
            setattr(self, key, value)
        
        # Initialize Config Booleans
        for key, default in self.config_booleans.items():
            value = (self._get_config_value(key, default, False)).lower() == "true"
            setattr(self, key, value)
        
        # Initialize String Secrets
        for key, default in self.config_string_secrets.items():
            value = self._get_config_value(key, default, True)
            setattr(self, key, value)

    def configure_logging(self):        
        # Reset logging handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Configure logger
        logging.basicConfig(
            level=self.LOGGING_LEVEL,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Suppress noisy http logging
        logging.getLogger("httpcore").setLevel(logging.WARNING)  
        logging.getLogger("httpx").setLevel(logging.WARNING)  

        # Log configuration
        logger.info(f"Configuration Initialized: {self.config_items}")
            
    def _get_config_value(self, name, default_value, is_secret):
        """Retrieve a configuration value, first from a file, then environment variable, then default."""
        value = default_value
        from_source = "default"

        # Check for config file first - try api_config folder first, then root
        api_config_path = Path(self.INPUT_FOLDER, "api_config", name)
        root_path = Path(self.INPUT_FOLDER, name)
        
        if api_config_path.exists():
            value = api_config_path.read_text().strip()
            from_source = "file"
        elif root_path.exists():
            value = root_path.read_text().strip()
            from_source = "file"
        # If no file, check for environment variable
        elif os.getenv(name):
            value = os.getenv(name)
            from_source = "environment"

        # Record the source of the config value
        self.config_items.append({
            "name": name,
            "value": "secret" if is_secret else value,
            "from": from_source
        })
        return value
    
    def _initialize_api_built_at(self):
        """Initialize API_BUILT_AT from the configurator directory."""
        import sys
        # Get the path to the configurator directory (where this file is located)
        configurator_dir = Path(__file__).parent.parent
        api_built_at_path = configurator_dir / "API_BUILT_AT"
        
        if api_built_at_path.exists():
            value = api_built_at_path.read_text().strip()
            from_source = "file"
        else:
            logger.fatal("API_BUILT_AT file is missing in the configurator directory. This value is required for API startup.")
            sys.exit(1)
        
        # Set the value
        self.API_BUILT_AT = value
        
        # Record the source
        self.config_items.append({
            "name": "API_BUILT_AT",
            "value": value,
            "from": from_source
        })
    
    # Serializer
    def to_dict(self):
        """Convert the Config object to a dictionary with the required fields."""
        return {
            "config_items": self.config_items,
        }    

    def assert_local(self):
        """Check if BUILT_AT is from file and has value 'Local', and MONGODB_REQUIRE_TLS is False. Raises ConfiguratorForbiddenException if not."""
        built_at_item = next((item for item in self.config_items if item['name'] == 'BUILT_AT'), None)
        if built_at_item is None:
            event = ConfiguratorEvent(event_id="CFG-ASSERT-01", event_type="ASSERT_LOCAL")
            event.record_failure("BUILT_AT configuration item not found")
            raise ConfiguratorForbiddenException("Write operations are only allowed when BUILT_AT is set to 'Local' from a file", event)
        
        is_local = built_at_item.get('from') == 'file' and built_at_item.get('value') == 'Local'
        if not is_local:
            event = ConfiguratorEvent(event_id="CFG-ASSERT-02", event_type="ASSERT_LOCAL")
            event.record_failure("BUILT_AT is not set to 'Local' from a file", {
                "source": built_at_item.get('from'),
                "value": built_at_item.get('value')
            })
            raise ConfiguratorForbiddenException("Write operations are only allowed when BUILT_AT is set to 'Local' from a file", event)
        
        # Check that MONGODB_REQUIRE_TLS is False for local environments
        require_tls_item = next((item for item in self.config_items if item['name'] == 'MONGODB_REQUIRE_TLS'), None)
        if require_tls_item is None:
            event = ConfiguratorEvent(event_id="CFG-ASSERT-03", event_type="ASSERT_LOCAL")
            event.record_failure("MONGODB_REQUIRE_TLS configuration item not found")
            raise ConfiguratorForbiddenException("Write operations are only allowed when MONGODB_REQUIRE_TLS is set to 'false' for local environments", event)
        
        require_tls_value = require_tls_item.get('value', '').lower() == 'true'
        if require_tls_value:
            event = ConfiguratorEvent(event_id="CFG-ASSERT-04", event_type="ASSERT_LOCAL")
            event.record_failure("MONGODB_REQUIRE_TLS is True but should be False for local environments", {
                "value": require_tls_item.get('value'),
                "source": require_tls_item.get('from')
            })
            raise ConfiguratorForbiddenException("Write operations are only allowed when MONGODB_REQUIRE_TLS is set to 'false' for local environments", event)
    
    # Singleton Getter
    @staticmethod
    def get_instance():
        """Get the singleton instance of the Config class."""
        if Config._instance is None:
            Config()
        
        return Config._instance
        