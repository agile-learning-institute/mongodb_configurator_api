from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException

class ServiceBase:
    def __init__(self, file_name: str = None, document: dict = None, folder_name: str = None):
        self.config = Config.get_instance()
        if file_name is None:
            service_name = self._folder_to_service_name(folder_name)
            event = ConfiguratorEvent(event_id=f"{service_name}-01", event_type=f"CREATE_{service_name.upper()}", event_data=document)
            raise ConfiguratorException(f"{service_name} file name is required", event)
        if document is None:
            document = FileIO.get_document(folder_name, file_name)
        self.file_name = file_name
        self._locked = document.get("_locked", False)
        self._folder_name = folder_name
        self._document = document  # Store the document for subclasses

    def to_dict(self):
        return {
            "file_name": self.file_name,
            "_locked": self._locked
        }

    def save(self):
        return FileIO.put_document(self._folder_name, self.file_name, self.to_dict())

    def delete(self):
        if self._locked:
            service_name = self._folder_to_service_name(self._folder_name)
            event = ConfiguratorEvent(event_id=f"{service_name}-02", event_type=f"DELETE_{service_name.upper()}")
            raise ConfiguratorException(f"Cannot delete locked {service_name}", event)
        return FileIO.delete_document(self._folder_name, self.file_name)

    @staticmethod
    def lock_all(service_class, status: bool = True):
        config = Config.get_instance()
        folder_name = service_class._get_folder_name()
        service_name = ServiceBase._folder_to_service_name(folder_name)
        
        lock_all_event = ConfiguratorEvent(event_id=f"{service_name}-03", event_type=f"LOCK_ALL_{service_name.upper()}S")
        file_event = None  # Initialize file_event to avoid UnboundLocalError
        file = None  # Initialize file to avoid UnboundLocalError
        try:
            for file in FileIO.get_documents(folder_name):
                file_event = ConfiguratorEvent(event_id=f"{service_name}-{file.file_name}", event_type=f"LOCK_{service_name.upper()}")
                lock_all_event.append_events([file_event])
                service_instance = service_class(file.file_name)
                service_instance._locked = status
                service_instance.save()
                file_event.record_success()
            lock_all_event.record_success()
            return lock_all_event
        except ConfiguratorException as e:
            lock_all_event.append_events([e.event])
            if file_event and file:
                file_event.record_failure(f"ConfiguratorException locking {service_name} {file.file_name}")
            lock_all_event.record_failure(f"ConfiguratorException locking {service_name} {file.file_name if file else 'unknown'}")
            raise ConfiguratorException(f"Cannot lock all {service_name}s", lock_all_event)
        except Exception as e:
            if file_event and file:
                file_event.record_failure(f"Unexpected error locking {service_name} {file.file_name}")
            lock_all_event.record_failure(f"Unexpected error locking {service_name} {file.file_name if file else 'unknown'}")
            raise ConfiguratorException(f"Cannot lock all {service_name}s", lock_all_event)

    @staticmethod
    def _get_folder_name():
        raise NotImplementedError

    @staticmethod
    def _folder_to_service_name(folder_name: str) -> str:
        """Convert folder name to service name"""
        if folder_name == "types":
            return "type"
        elif folder_name == "dictionaries":
            return "dictionary"
        elif folder_name == "enumerators":
            return "enumerator"
        elif folder_name == "configurations":
            return "configuration"
        else:
            # Fallback: remove 's' from end if present
            return folder_name.rstrip('s') 