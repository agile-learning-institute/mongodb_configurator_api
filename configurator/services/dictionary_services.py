import os
from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.configurator_exception import ConfiguratorException, ConfiguratorEvent
from configurator.services.enumerator_service import Enumerations
from configurator.services.property import Property

class Dictionary:
    def __init__(self, file_name: str = None, document: dict = None):
        self.config = Config.get_instance()
        if file_name is None:
            event = ConfiguratorEvent(event_id="DIC-01", event_type="CREATE_DICTIONARY", event_data=document)
            raise ConfiguratorException("Dictionary file name is required", event)
        
        if document is None:
            document = FileIO.get_document(self.config.DICTIONARY_FOLDER, file_name)
            
        self.file_name = file_name
        self._locked = False        
        self.root = Property(document)

    def to_dict(self):
        result = {}
        result["file_name"] = self.file_name
        result["_locked"] = self._locked
        result["root"] = self.root.to_dict()
        return result

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        return self.root.get_json_schema(enumerations, ref_stack)

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        return self.root.get_bson_schema(enumerations, ref_stack)

    def save(self):
        return FileIO.put_document(self.config.DICTIONARY_FOLDER, self.file_name, self.to_dict())

    def delete(self):
        if self._locked:
            event = ConfiguratorEvent(event_id="DIC-02", event_type="DELETE_DICTIONARY", event_data={"error": "Dictionary is locked"})
            raise ConfiguratorException("Cannot delete locked dictionary", event)
        return FileIO.delete_document(self.config.DICTIONARY_FOLDER, self.file_name)

    @staticmethod
    def lock_all(status: bool = True):
        try:
            config = Config.get_instance()
            lock_all_event = ConfiguratorEvent(event_id="DIC-03", event_type="LOCK_ALL_DICTIONARIES")
            for file in FileIO.get_documents(config.DICTIONARY_FOLDER):
                file_event = ConfiguratorEvent(event_id=f"DIC-{file.file_name}", event_type="LOCK_DICTIONARY")
                lock_all_event.append_events([file_event])
                dictionary = Dictionary(file.file_name)
                dictionary._locked = status
                dictionary.save()
                file_event.record_success()
            lock_all_event.record_success()
            return lock_all_event
        except ConfiguratorException as e:
            lock_all_event.append_events([e.event])
            file_event.record_failure(f"ConfiguratorException locking dictionary {self.version_number}")
            lock_all_event.record_failure(f"ConfiguratorException locking all dictionaries: {str(e)}")
            raise ConfiguratorException("Cannot lock all dictionaries", lock_all_event)
        except Exception as e:
            file_event.record_failure(f"Unexpected error locking all dictionaries: {str(e)}")
            lock_all_event.record_failure(f"Unexpected error locking all dictionaries: {str(e)}")
            raise ConfiguratorException("Cannot lock all dictionaries", lock_all_event)
