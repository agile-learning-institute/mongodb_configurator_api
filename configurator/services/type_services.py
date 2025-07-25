import os
import yaml
from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.services.property import Property
from configurator.services.enumerator_service import Enumerations

class Type:
    def __init__(self, file_name: str, document: dict = None):
        self.config = Config.get_instance()
        if file_name is None:
            event = ConfiguratorEvent(event_id="TYP-01", event_type="CREATE_TYPE", event_data=document)
            raise ConfiguratorException("Type file name is required", event)
        
        if document is None:
            document = FileIO.get_document(self.config.TYPE_FOLDER, file_name)

        self.file_name = file_name
        self._locked = document.get("_locked", False)
        self.root = Property(document.get("root", {}))

    def to_dict(self):
        the_dict = {}
        the_dict['file_name'] = self.file_name
        the_dict['_locked'] = self._locked
        the_dict['root'] = self.root.to_dict()
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        return self.root.to_json_schema(enumerations, ref_stack)
    
    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        return self.root.to_bson_schema(enumerations, ref_stack)
    
    def save(self):
        return FileIO.put_document(self.config.TYPE_FOLDER, self.file_name, self.to_dict())
                
    def delete(self):
        if self._locked:
            event = ConfiguratorEvent(event_id="TYP-02", event_type="DELETE_TYPE")
            raise ConfiguratorException("Cannot delete locked type", event)
        return FileIO.delete_document(self.config.TYPE_FOLDER, self.file_name)

    @staticmethod
    def lock_all(status: bool = True):
        try:
            config = Config.get_instance()
            lock_all_event = ConfiguratorEvent(event_id="TYP-03", event_type="LOCK_ALL_TYPES", event_data={"status": status})
            for file in FileIO.get_documents(config.TYPE_FOLDER):
                file_event = ConfiguratorEvent(event_id=f"TYP-{file.file_name}", event_type="LOCK_TYPE")
                lock_all_event.append_events([file_event])
                type = Type(file.file_name)            
                type._locked = status
                type.save()                
                file_event.record_success()
            lock_all_event.record_success()
            return lock_all_event
        except ConfiguratorException as e:
            lock_all_event.append_events([e.event])
            lock_all_event.record_failure(f"ConfiguratorException locking all types: {str(e)}") 
            raise ConfiguratorException("Cannot lock all types", lock_all_event)
        except Exception as e:
            lock_all_event.record_failure(f"Unexpected error locking all types: {str(e)}")
            raise ConfiguratorException("Cannot lock all types", lock_all_event)

