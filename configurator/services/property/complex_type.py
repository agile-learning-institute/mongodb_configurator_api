from configurator.services.enumeration_service import Enumerations
from .base import BaseProperty

class ComplexType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.bson_schema = data.get("bson_schema", {})
        self.json_schema = data.get("json_schema", {})

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['bson_schema'] = self.bson_schema
        the_dict['json_schema'] = self.json_schema
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema.update(self.json_schema)
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema.update(self.bson_schema)
        return the_schema

