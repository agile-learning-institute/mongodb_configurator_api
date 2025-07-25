from configurator.services.enumerator_service import Enumerations
from .property import Property

class EnumType(Property):
    def __init__(self, data: dict):
        super().__init__(data)
        self.enums = data.get('enums', 'void')

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['enums'] = self.enums
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema()
        the_schema['type'] = 'string'
        the_schema['enum'] = enumerations.get_enumerations(self.enums)
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema()
        the_schema['bsonType'] = 'string'
        the_schema['enum'] = enumerations.get_enumerations(self.enums)
        return the_schema

