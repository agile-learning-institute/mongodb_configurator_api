from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.utils.config import Config
from configurator.services.service_base import ServiceBase
from typing import List, Dict

class Enumerations(ServiceBase):
    def __init__(self, file_name: str = None, document: dict = None):
        super().__init__(file_name, document, Config.get_instance().ENUMERATOR_FOLDER)
        self.name = self._document.get("name")
        self.values = []
        for value in self._document.get("values", []):
            self.values.append({
                "value": value.get("value"),
                "description": value.get("description")
            })
            
        self._locked = self._document.get("_locked", False)

    def to_dict(self):
        d = super().to_dict()
        d["name"] = self.name
        d["values"] = []
        for value in self.values:
            d["values"].append({
                "value": value.get("value"),
                "description": value.get("description")
            })
        return d

    def get_enum_dict(self) -> Dict[str, Dict[str, str]]:
        the_dict = {}
        for value in self.values:
            the_dict[value.get("value")] = value.get("description")
        return the_dict

    def get_enum_values(self, enum_name: str) -> List[str]:
        the_values = set()
        for value in self.values:
            the_values.add(value.get("value"))
        return the_values 