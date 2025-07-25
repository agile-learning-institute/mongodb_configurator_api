from configurator.services.enumerator_service import Enumerations
from .base import BaseProperty
from configurator.services.dictionary_services import Dictionary

class RefType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.ref = data.get("ref", "")

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['ref'] = self.ref
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        dictionary = Dictionary(self.ref)
        the_schema = dictionary.to_json_schema(enumerations, ref_stack)
        return the_schema

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        dictionary = Dictionary(self.ref)
        the_schema = dictionary.to_bson_schema(enumerations, ref_stack)
        return the_schema

