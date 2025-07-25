from configurator.services.enumerator_service import Enumerations
from .property import BaseProperty, create_property

class OneOfType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.one_of = []
        for property in data.get("oneOf", []):
            self.one_of.append(create_property(property))

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['oneOf'] = [property.to_dict() for property in self.one_of]
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema['oneOf'] = [property.to_json_schema(enumerations, ref_stack) for property in self.one_of]
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema['oneOf'] = [property.to_bson_schema(enumerations, ref_stack) for property in self.one_of]
        return the_schema
