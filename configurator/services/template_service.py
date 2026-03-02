import os
from pathlib import Path
import yaml

from configurator.services.configuration_services import Configuration
from configurator.services.dictionary_services import Dictionary
from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException

import logging
logger = logging.getLogger(__name__)

# Version for new collections
NEW_COLLECTION_VERSION = "1.0.0.0"


def _load_configuration_template(collection_name: str) -> dict:
    """
    Load the configuration template (add_indexes for initial version).
    Override: {INPUT_FOLDER}/{API_CONFIG_FOLDER}/templates/default_new_configuration.yaml
    Built-in: configurator/templates/default_new_configuration.yaml
    """
    config = Config.get_instance()
    override_path = Path(config.INPUT_FOLDER, config.API_CONFIG_FOLDER, "templates", "default_new_configuration.yaml")

    if override_path.exists():
        with open(override_path, "r", encoding="utf-8") as f:
            template_content = yaml.safe_load(f)
    else:
        configurator_dir = Path(__file__).parent.parent
        builtin_path = configurator_dir / "templates" / "default_new_configuration.yaml"
        with open(builtin_path, "r", encoding="utf-8") as f:
            template_content = yaml.safe_load(f)

    content_str = yaml.dump(template_content)
    content_str = content_str.replace("{{collection_name}}", collection_name)
    return yaml.safe_load(content_str)


def _load_dictionary_template(collection_name: str, description: str = "") -> dict:
    """
    Load the dictionary template. Checks api_config path first, then built-in default.
    Override: {INPUT_FOLDER}/{API_CONFIG_FOLDER}/templates/default_new_dictionary.yaml
    Built-in: configurator/templates/default_new_dictionary.yaml (simple root with type: void)
    """
    config = Config.get_instance()
    override_path = Path(config.INPUT_FOLDER, config.API_CONFIG_FOLDER, "templates", "default_new_dictionary.yaml")

    if override_path.exists():
        with open(override_path, "r", encoding="utf-8") as f:
            template_content = yaml.safe_load(f)
    else:
        # Built-in default: bundled in package
        configurator_dir = Path(__file__).parent.parent
        builtin_path = configurator_dir / "templates" / "default_new_dictionary.yaml"
        with open(builtin_path, "r", encoding="utf-8") as f:
            template_content = yaml.safe_load(f)

    # Substitute placeholders
    content_str = yaml.dump(template_content)
    content_str = content_str.replace("{{collection_name}}", collection_name)
    content_str = content_str.replace("{{description}}", description or f"A {collection_name} collection")
    return yaml.safe_load(content_str)


class TemplateService:
    def __init__(self):
        pass

    @staticmethod
    def create_collection(collection_name: str, description: str = "") -> dict:
        config = Config.get_instance()
        configuration_file_name = f"{collection_name}.yaml"
        dictionary_file_name = f"{collection_name}.1.0.0.yaml"
        test_data_file_name = f"{collection_name}.1.0.0.0.json"

        if FileIO.file_exists(config.CONFIGURATION_FOLDER, configuration_file_name):
            event = ConfiguratorEvent("TEMPLATE-01", "CONFIGURATION_EXISTS", {"file": configuration_file_name})
            raise ConfiguratorException(f"Configuration file {configuration_file_name} already exists", event)

        if FileIO.file_exists(config.DICTIONARY_FOLDER, dictionary_file_name):
            event = ConfiguratorEvent("TEMPLATE-02", "DICTIONARY_EXISTS", {"file": dictionary_file_name})
            raise ConfiguratorException(f"Dictionary file {dictionary_file_name} already exists", event)

        # 1. Create configuration
        configuration_template = TemplateService._new_configuration(
            collection_name, configuration_file_name, test_data_file_name, description
        )
        configuration_template.save()

        # 2. Create dictionary from template
        dictionary_template = TemplateService._new_dictionary(
            collection_name, dictionary_file_name, description
        )
        dictionary_template.save()

        # 3. Create test_data file (empty array)
        FileIO.put_document(config.TEST_DATA_FOLDER, test_data_file_name, [])

        return {
            "configuration_file": configuration_file_name,
            "dictionary_file": dictionary_file_name,
            "test_data_file": test_data_file_name,
            "version": NEW_COLLECTION_VERSION,
        }

    @staticmethod
    def _new_configuration(collection_name: str, file_name: str, test_data_file_name: str, description: str = ""):
        config_template = _load_configuration_template(collection_name)
        add_indexes = config_template.get("add_indexes", [])

        document = {
            "file_name": file_name,
            "title": f"{collection_name} Configuration",
            "description": description or f"Collection for managing {collection_name}",
            "versions": [
                {
                    "version": NEW_COLLECTION_VERSION,
                    "test_data": test_data_file_name,
                    "migrations": [],
                    "add_indexes": add_indexes,
                    "drop_indexes": [],
                }
            ],
        }
        return Configuration(file_name, document)

    @staticmethod
    def _new_dictionary(collection_name: str, file_name: str, description: str = ""):
        root_data = _load_dictionary_template(collection_name, description)
        root_data["name"] = root_data.get("name", "root")
        document = {
            "file_name": file_name,
            "_locked": False,
            "root": root_data,
        }
        return Dictionary(file_name, document)
