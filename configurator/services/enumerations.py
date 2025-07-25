from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.utils.file_io import FileIO, File
from configurator.utils.config import Config
from configurator.utils.mongo_io import MongoIO
import os
from typing import List, Dict, Any, Optional

class Enumerations:
    def __init__(self, enumeration: dict = {}):
        self.config = Config.get_instance()
        self.name = enumeration.get("name")
        self.values = []
        for value in enumeration.get("values", []):
            self.values.append({
                "value": value.get("value"),
                "description": value.get("description")
            })
            
        self._locked = enumeration.get("_locked", False)

    def to_dict(self):
        the_dict = {}
        the_dict["name"] = self.name
        the_dict["values"] = []
        for value in self.values:
            the_dict["values"].append({
                "value": value.get("value"),
                "description": value.get("description")
            })
        return the_dict

    def get_enum_dict(self) -> Dict[str, Dict[str, str]]:
        the_dict = {}
        for value in self.values:
            the_dict[value.get("name")] = value.get("description")
        return the_dict

    def get_enum_values(self, enum_name: str) -> List[str]:
        the_values = set()
        for value in self.values:
            the_values.add(value.get("value"))
        return the_values
    