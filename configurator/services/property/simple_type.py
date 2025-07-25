from configurator.services.enumerator_service import Enumerations
from .base import BaseProperty

class SimpleType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.schema = data.get("schema", {})

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['schema'] = self.schema
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_dict = super().to_json_schema(enumerations, ref_stack)
        the_dict.update(self.schema)
        return the_dict

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_dict = super().to_bson_schema(enumerations, ref_stack)
        the_dict.update(self.schema)
        the_dict["bsonType"] = the_dict["type"]
        del the_dict["type"]
        return the_dict

