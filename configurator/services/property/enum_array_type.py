from configurator.services.enumerator_service import Enumerations
from configurator.services.property import Property

class EnumArrayType(Property):
    def __init__(self, data: dict):
        super().__init__(data)
        self.enums = data.get('enums', 'void')

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['enums'] = self.enums
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_json_schema()
        the_schema['type'] = 'array'
        the_schema['items'] = {
            'type': 'string',
            'enum': enumerations.get_enumerations(self.enums)
        }
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        the_schema = super().to_bson_schema()
        the_schema['bsonType'] = 'array'
        the_schema['items'] = {
            'type': 'string',
            'enum': enumerations.get_enumerations(self.enums)
        }
        return the_schema

