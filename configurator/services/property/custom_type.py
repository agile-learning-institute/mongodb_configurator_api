from configurator.services.enumerator_service import Enumerations
from .property import BaseProperty

class CustomType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.custom_schema = data.get("schema", {})

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['schema'] = self.custom_schema
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema.update(self.custom_schema)
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema.update(self.custom_schema)
        return the_schema
