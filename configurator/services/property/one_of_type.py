from configurator.services.enumerator_service import Enumerations
from .property import Property

class OneOfType(Property):
    def __init__(self, data: dict):
        super().__init__(data)
        self.properties = []
        for property in data.get('properties', []):
            self.properties.append(Property(property))

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['one_of'] = [property.to_dict() for property in self.properties]
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema['properties'] = [property.to_json_schema(enumerations, ref_stack) for property in self.properties]
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema['properties'] = [property.to_bson_schema(enumerations, ref_stack) for property in self.properties]
        return the_schema
