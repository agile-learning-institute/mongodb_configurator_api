from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException

class ServiceBase:
    def __init__(self, file_name: str = None, document: dict = None, folder_name: str = None):
        self.config = Config.get_instance()
        if file_name is None:
            event = ConfiguratorEvent(event_id="BASE_01", event_type=f"CREATE_{folder_name}", event_data=document)
            raise ConfiguratorException(f"{folder_name} file name is required", event)
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
            event = ConfiguratorEvent(event_id=f"{self._folder_name}-02", event_type=f"DELETE_{self._folder_name.upper()}")
            raise ConfiguratorException(f"Cannot delete locked {self._folder_name}", event)
        return FileIO.delete_document(self._folder_name, self.file_name)

    @staticmethod
    def lock_all(service_class, folder_name: str, status: bool = True):
        config = Config.get_instance()
        lock_all_event = ConfiguratorEvent(event_id=f"{folder_name}-03", event_type=f"LOCK_ALL_{folder_name.upper()}S")
        file_event = ConfiguratorEvent(event_id="SVC-03", event_type=f"PREPARE_LOCK_ALL")
        try:
            for file in FileIO.get_documents(folder_name):
                file_event = ConfiguratorEvent(event_id=f"{folder_name}-{file.file_name}", event_type=f"LOCK_{folder_name.upper()}")
                lock_all_event.append_events([file_event])
                service_instance = service_class(file.file_name)
                service_instance._locked = status
                service_instance.save()
                file_event.record_success()
            lock_all_event.record_success()
            return lock_all_event
        except ConfiguratorException as e:
            lock_all_event.append_events([e.event])
            file_event.record_failure(f"ConfiguratorException locking {folder_name}")
            lock_all_event.record_failure(f"ConfiguratorException locking {folder_name}")
            raise ConfiguratorException(f"Cannot lock all {folder_name}s", lock_all_event)
        except Exception as e:
            file_event.record_failure(f"Unexpected error locking {folder_name}")
            lock_all_event.record_failure(f"Unexpected error locking {folder_name}")
            raise ConfiguratorException(f"Cannot lock all {folder_name}s", lock_all_event)
