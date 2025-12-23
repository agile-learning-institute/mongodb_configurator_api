from configurator.services.enumeration_service import Enumerations
from .base import BaseProperty
from .property import Property

class ArrayType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        items_data = data.get("items", {})
        items_data = {**items_data, "name": items_data.get("name", "items")}
        self.items = Property(items_data)

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['items'] = self.items.to_dict()
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema['items'] = self.items.to_json_schema(enumerations, ref_stack)
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema['items'] = self.items.to_bson_schema(enumerations, ref_stack)
        return the_schema
