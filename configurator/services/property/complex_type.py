from configurator.services.enumeration_service import Enumerations
from .base import BaseProperty

class ComplexType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.bson_type = data.get("bson_type", {})
        self.json_type = data.get("json_type", {})

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['bson_type'] = self.bson_type
        the_dict['json_type'] = self.json_type
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema.update(self.json_type)
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema.update(self.bson_type)
        return the_schema

