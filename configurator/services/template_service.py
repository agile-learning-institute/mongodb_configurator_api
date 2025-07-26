from configurator.services.configuration_services import Configuration
from configurator.services.dictionary_services import Dictionary
from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
import yaml

class TemplateService:
    def __init__(self):
        pass
    
    @staticmethod
    def create_collection(collection_name: str) -> dict:
        config = Config.get_instance()
        configuration_file_name = f"{collection_name}.yaml"
        dictionary_file_name = f"{collection_name}.0.0.1.yaml"
        configuration_template = TemplateService.new_configuration(collection_name, configuration_file_name)
        dictionary_template = TemplateService.new_dictionary(collection_name, dictionary_file_name)
        
        if FileIO.file_exists(config.CONFIGURATION_FOLDER, configuration_file_name):
            event = ConfiguratorEvent("TEMPLATE-01", "CONFIGURATION_EXISTS", {"file": configuration_file_name})
            raise ConfiguratorException(f"Configuration file {configuration_file_name} already exists", event)
        
        if FileIO.file_exists(config.DICTIONARY_FOLDER, dictionary_file_name):
            event = ConfiguratorEvent("TEMPLATE-02", "DICTIONARY_EXISTS", {"file": dictionary_file_name})
            raise ConfiguratorException(f"Dictionary file {dictionary_file_name} already exists", event)
        
        configuration_template.save()
        dictionary_template.save()
                
    @staticmethod
    def new_configuration(collection_name: str, file_name: str = None):
        document = {}
        document["file_name"] = file_name
        document["title"] = f"{collection_name} Configuration"
        document["description"] = f"Collection for managing {collection_name}"
        document["versions"] = [{"version": "0.0.1.0"}]
        return Configuration(file_name, document)
    
    @staticmethod
    def new_dictionary(collection_name: str, file_name: str = None):
        document = {}
        document["file_name"] = file_name
        document["root"] = {}
        document["root"]["name"] = "root"
        document["root"]["description"] = f"A {collection_name} collection for testing the schema system"
        document["root"]["type"] = "object"
        document["root"]["properties"] = [
            {
                "name": "_id",
                "description": "A unique identifier",
                "type": "identifier",
                "required": True
            }, {
                "name": "name",
                "description": "The name",
                "type": "word",
                "required": True
            }, {
                "name": "status",
                "description": "The current status",
                "type": "enum",
                "enums": "default_status",
                "required": True
            }, {
                "name": "last_saved",
                "description": "The last time this document was saved",
                "type": "breadcrumb",
                "required": True
            }
        ]
        return Dictionary(file_name, document)
