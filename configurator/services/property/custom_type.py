from configurator.services.enumerator_service import Enumerations
from configurator.services.property import Property
from configurator.services.type_services import Type

class CustomType(Property):
    def __init__(self, data: dict):
        super().__init__(data)

    def to_dict(self):
        the_dict = super().to_dict()
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        type = Type(file_name=f"{self.type}.yaml")
        the_schema = super().to_json_schema()
        the_schema.update(type.to_json_schema(enumerations, ref_stack))
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        type = Type(file_name=f"{self.type}.yaml")
        the_schema = super().to_bson_schema()
        the_schema.update(type.to_bson_schema(enumerations, ref_stack))
        return the_schema
