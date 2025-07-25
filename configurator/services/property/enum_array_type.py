from configurator.services.enumerator_service import Enumerations
from .base import BaseProperty

class EnumArrayType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.enum_name = data.get("enum", "")

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['enum'] = self.enum_name
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema['type'] = 'array'
        the_schema['items'] = {'type': 'string', 'enum': enumerations.get_enum_values(self.enum_name)}
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema['bsonType'] = 'array'
        the_schema['items'] = {'bsonType': 'string', 'enum': enumerations.get_enum_values(self.enum_name)}
        return the_schema

