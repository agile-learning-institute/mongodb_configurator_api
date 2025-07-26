from configurator.services.enumerations import Enumerations
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.utils.file_io import FileIO, File
from configurator.utils.config import Config
from configurator.utils.mongo_io import MongoIO
from configurator.services.service_base import ServiceBase
import os
from typing import List, Dict, Any, Optional

class Enumerators(ServiceBase):
    """A list of Enumerations - loads enumerations on demand"""
    def __init__(self, file_name: str = None, document: dict = None):
        super().__init__(file_name, document, Config.get_instance().ENUMERATOR_FOLDER)
        self.version = self._document.get("version", 0)
        self.enumerations = []
        for enumeration in self._document.get("enumerators", []):
            self.enumerations.append(Enumerations(enumeration))

    def to_dict(self):
        d = super().to_dict()
        d["enumerations"] = [enumeration.to_dict() for enumeration in self.enumerations]
        return d

    def upsert_all_to_database(self, mongo_io: MongoIO) -> ConfiguratorEvent:
        config = Config.get_instance()

        try:
            upsert_all_event = ConfiguratorEvent("ENU-02", "UPSERT_ENUMERATORS_TO_DATABASE")
            for enumeration in self.enumerations:
                enumeration_event = ConfiguratorEvent(f"ENU-UPSERT-{enumeration.file_name}", "UPSERT_ENUMERATION")
                upsert_all_event.append_events([enumeration_event])
                enumeration.upsert(mongo_io)
                enumeration_event.record_success()
            upsert_all_event.record_success()
            return upsert_all_event
        except ConfiguratorException as e:
            enumeration_event.record_failure(f"ConfiguratorException upserting enumerator {enumeration.file_name}")
            upsert_all_event.append_events([e.event])
            upsert_all_event.record_failure(f"ConfiguratorException upserting enumerator {self.file_name}")
            raise ConfiguratorException("Cannot upsert all enumerators", upsert_all_event)
        except Exception as e:
            enumeration_event.record_failure(f"Unexpected error upserting enumerator {enumeration.file_name}")
            upsert_all_event.record_failure(f"Unexpected error upserting enumerator {self.file_name}")
            raise ConfiguratorException("Cannot upsert all enumerators", upsert_all_event)

    def getVersion(self, version_number: int):
        for enumeration in self.enumerations:
            if enumeration.version == version_number:
                return enumeration
        
        event = ConfiguratorEvent("ENU-03", "GET_VERSION")
        event.record_failure(f"Version {version_number} not found")
        raise ConfiguratorException(f"Version {version_number} not found", event)

    @staticmethod
    def lock_all(status: bool = True):
        return ServiceBase.lock_all(Enumerators, Config.get_instance().ENUMERATOR_FOLDER, status)

