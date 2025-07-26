from configurator.services.enumeration_service import Enumerations
from .base import BaseProperty
from .property import Property

class ObjectType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.additional_properties = data.get("additionalProperties", False)
        self.properties = []
        for property in data.get("properties", []):
            self.properties.append(Property(property))

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['additionalProperties'] = self.additional_properties
        the_dict['properties'] = [property.to_dict() for property in self.properties]
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema(enumerations, ref_stack)
        the_schema['additionalProperties'] = self.additional_properties
        the_schema['properties'] = {prop.name: prop.to_json_schema(enumerations, ref_stack) for prop in self.properties}
        the_schema['required'] = [prop.name for prop in self.properties if prop.required]   
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema(enumerations, ref_stack)
        the_schema['additionalProperties'] = self.additional_properties
        the_schema['properties'] = {prop.name: prop.to_bson_schema(enumerations, ref_stack) for prop in self.properties}
        the_schema['required'] = [prop.name for prop in self.properties if prop.required]
        return the_schema 