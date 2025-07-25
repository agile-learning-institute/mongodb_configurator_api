from configurator.services.enumerations import Enumerations
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.utils.file_io import FileIO, File
from configurator.utils.config import Config
from configurator.utils.mongo_io import MongoIO
import os
from typing import List, Dict, Any, Optional

class Enumerators:
    """A list of Enumerations - loads enumerations on demand"""
    def __init__(self, file_name: str = None, document: dict = None):
        self.config = Config.get_instance()
        if file_name is None:
            event = ConfiguratorEvent(event_id="ENU-01", event_type="CREATE_ENUMERATORS", event_data=document)
            raise ConfiguratorException("Enumerator file name is required", event)
        
        if document is None:
            document = FileIO.get_document(self.config.ENUMERATOR_FOLDER, file_name)
        
        self.file_name = file_name
        self._locked = document.get("_locked", False)
        self.version = document.get("version", 0)
        self.enumerations = []
        for enumeration in document.get("enumerators", []):
            self.enumerations.append(Enumerations(enumeration))

    def to_dict(self):
        the_dict = {}
        the_dict["file_name"] = self.file_name
        the_dict["_locked"] = self._locked
        the_dict["enumerations"] = [enumeration.to_dict() for enumeration in self.enumerations]
        return the_dict
    
    def save(self):
        return FileIO.put_document(self.config.ENUMERATOR_FOLDER, self.file_name, self.to_dict())
    
    def delete(self):
        if self._locked:
            event = ConfiguratorEvent(event_id="ENU-02", event_type="DELETE_ENUMERATORS", event_data={"error": "Enumerator is locked"})
            raise ConfiguratorException("Cannot delete locked enumerator", event)
        
        return FileIO.delete_document(self.config.ENUMERATOR_FOLDER, self.file_name)
    
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
        try:
            config = Config.get_instance()
            lock_all_event = ConfiguratorEvent("ENU-04", "LOCK_ENUMERATIONS")
            for file in FileIO.get_documents(config.ENUMERATORS_FOLDER):
                file_event = ConfiguratorEvent(f"ENU-{file.file_name}", "LOCK_ENUMERATION")
                lock_all_event.append_events([file_event])
                enumerator = Enumerators(file.file_name)
                enumerator._locked = status
                enumerator.save()
                file_event.record_success()
            lock_all_event.record_success()
            return lock_all_event
        except ConfiguratorException as e:
            lock_all_event.append_events([e.event])
            file_event.record_failure(f"ConfiguratorException locking enumerator {file.file_name}")
            lock_all_event.record_failure(f"ConfiguratorException locking enumerator {file.file_name}")
            raise ConfiguratorException("Cannot lock all enumerators", lock_all_event)
        except Exception as e:
            file_event.record_failure(f"Unexpected error locking enumerator {file.file_name}")
            lock_all_event.record_failure(f"Unexpected error locking enumerator {file.file_name}")
            raise ConfiguratorException("Cannot lock all enumerators", lock_all_event)

