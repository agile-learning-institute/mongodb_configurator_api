from configurator.utils.file_io import FileIO
from configurator.utils.config import Config
from configurator.services.enumerator_service import Enumerations
from .object_type import ObjectType
from .array_type import ArrayType
from .complex_type import ComplexType
from .simple_type import SimpleType
from .custom_type import CustomType
from .enum_array_type import EnumArrayType
from .enum_type import EnumType
from .one_of_type import OneOfType
from .ref_type import RefType
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException

class Property:
    def __new__(cls, data: dict):
        type_ = data.get('type', 'void')
        if type_ == 'array':
            return ArrayType(data)
        elif type_ == 'complex':
            return ComplexType(data)
        elif type_ == 'enum_array':
            return EnumArrayType(data)
        elif type_ == 'enum':
            return EnumType(data)
        elif type_ == 'object':
            return ObjectType(data)
        elif type_ == 'one_of':
            return OneOfType(data)
        elif type_ == 'ref':
            return RefType(data)
        elif type_ == 'simple':
            return SimpleType(data)
        else:
            return CustomType(data)

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
        the_dict = {}
        the_dict['name'] = self.name
        the_dict['description'] = self.description
        the_dict['type'] = self.type
        the_dict['required'] = self.required
        return the_dict
    
    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = {}
        the_schema['description'] = self.description
        the_schema['type'] = self.type
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = {}
        the_schema['bsonType'] = self.type
        return the_schema 