from configurator.services.enumeration_service import Enumerations
from .base import BaseProperty
from configurator.services.type_services import Type

class ConstantType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.constant = data.get("constant", "")

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict["constant"] = self.constant
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema['type'] = 'string'
        the_schema['const'] = self.constant
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema['bsonType'] = 'string'
        the_schema['const'] = self.constant
        return the_schema
