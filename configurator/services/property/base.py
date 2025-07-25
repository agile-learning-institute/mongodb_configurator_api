"""Base class for all property types"""

from configurator.utils.config import Config
from configurator.services.enumerator_service import Enumerations
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException

class BaseProperty:
    """Base class for all property types"""
    
    def __init__(self, data: dict):
        self.config = Config.get_instance()
        if 'name' not in data:
            event = ConfiguratorEvent(event_id="TYP-01", event_type="MISSING_NAME", event_data=data)
            raise ConfiguratorException("Missing required name", event)

        self.name = data.get('name')
        self.description = data.get('description', '')
        self.type = data.get('type', 'void')
        self.required = data.get('required', False)

    def to_dict(self):
        """Convert property to dictionary"""
        the_dict = {}
        the_dict['name'] = self.name
        the_dict['description'] = self.description
        the_dict['type'] = self.type
        the_dict['required'] = self.required
        return the_dict
    
    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        """Convert to JSON schema format"""
        the_schema = {}
        the_schema['description'] = self.description
        the_schema['type'] = self.type
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        """Convert to BSON schema format"""
        the_schema = {}
        the_schema['bsonType'] = self.type
        return the_schema 