from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.utils.config import Config
from configurator.services.service_base import ServiceBase
from configurator.utils.version_number import VersionNumber
from typing import List, Dict

from configurator.utils.mongo_io import MongoIO

class Enumerations(ServiceBase):
    def __init__(self, file_name: str = None, document: dict = None):
        super().__init__(file_name, document, Config.get_instance().ENUMERATOR_FOLDER)
        self.version = self._document.get("version", 0)
        self.enumerators = self._document.get("enumerators", [])

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict["version"] = self.version
        the_dict["enumerators"] = self.enumerators
        return the_dict

    def get_enum_values(self, enum_name: str) -> List[str]:
        the_values = set()
        for enumeration in self.enumerators:
            if enumeration.get("name") == enum_name:
                for value in enumeration.get("values"): 
                    the_values.add(value.get("value"))
                return sorted(list(the_values)) 

        event = ConfiguratorEvent(event_id=f"ENU-02", event_type="ERROR", event_data=self.to_dict())
        event.record_failure(f"Enumeration {enum_name} not found")
        raise ConfiguratorException(f"Enumeration {enum_name} not found", event)
    
    def upsert(self, mongo_io: MongoIO) -> ConfiguratorEvent:
        event = ConfiguratorEvent(event_id=f"ENU-01-{self.file_name}", event_type="PROCESS", event_data=self.to_dict())
        mongo_io.upsert(self.config.ENUMERATORS_COLLECTION_NAME, {"version": self.version}, self.to_dict())
        event.record_success()
        return event
    
    @staticmethod
    def lock_all(status: bool = True):
        return ServiceBase.lock_all(Enumerations, Config.get_instance().ENUMERATOR_FOLDER, status)
    