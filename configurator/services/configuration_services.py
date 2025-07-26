from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.mongo_io import MongoIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.services.configuration_version import Version
from configurator.services.enumerator_service import Enumerators

class Configuration:
    def __init__(self, file_name: str = None, document: dict = None):
        self.config = Config.get_instance()
        
        if file_name is None:
            event = ConfiguratorEvent(event_id="CFG-01", event_type="CREATE_CONFIGURATION", event_data=document)
            raise ConfiguratorException("Configuration file name is required", event)
        
        if document is None:
            document = FileIO.get_document(self.config.CONFIGURATION_FOLDER, file_name)

        self.file_name = file_name
        self.collection_name = file_name.split('.')[0]
        self._locked = document.get("_locked", False)
        self.title = document.get("title", "")
        self.description = document.get("description", "")
        self.versions = [Version(self.collection_name, document) for v in document.get("versions", [])]

    def to_dict(self):
        the_dict = {}
        the_dict["file_name"] = self.file_name
        the_dict["_locked"] = self._locked
        the_dict["title"] = self.title
        the_dict["description"] = self.description
        the_dict["versions"] = [v.to_dict() for v in self.versions]
        return the_dict

    def get_json_schema(self, version_str: str) -> dict:
        for version in self.versions:
            if version.version_str == version_str:
                enumerations = Enumerators().getVersion(version.collection_version.get_enumerator_version())
                return version.get_json_schema(enumerations)
        
        event = ConfiguratorEvent("CFG-02", "GET_JSON_SCHEMA")
        event.record_failure(f"Version {version_str} not found")
        raise ConfiguratorException(f"Version {version_str} not found", event)

    def get_bson_schema(self, version_str: str) -> dict:
        """Get BSON schema for a specific version."""
        for version in self.versions:
            if version.version_str == version_str:
                enumerations = Enumerators().getVersion(version.collection_version.get_enumerator_version())
                return version.get_bson_schema(enumerations)
        
        event = ConfiguratorEvent("CFG-03", "GET_BSON_SCHEMA")
        event.record_failure(f"Version {version_str} not found")
        raise ConfiguratorException(f"Version {version_str} not found", event)

    def save(self):
        return FileIO.put_document(self.config.CONFIGURATION_FOLDER, self.file_name, self.to_dict())
    
    def delete(self):
        if self._locked:
            event = ConfiguratorEvent(event_id="CFG-04", event_type="DELETE_CONFIGURATION")
            event.record_failure("Cannot delete locked configuration")
            raise ConfiguratorException("Cannot delete locked configuration", event)

        return FileIO.delete_document(self.config.CONFIGURATION_FOLDER, self.file_name)
        
    def process(self) -> ConfiguratorEvent:
        try:
            event = ConfiguratorEvent(event_id=f"CFG-05", event_type="PROCESS_CONFIGURATION")
            event.data = {"configuration_name": self.file_name, "version_count": len(self.versions)}
            mongo_io = MongoIO(self.config.MONGO_CONNECTION_STRING, self.config.MONGO_DB_NAME)

            enumerators = Enumerators()
            event.append_events(enumerators.upsert_all_to_database(mongo_io))        
            for version in self.versions:
                event.append_events([version.process(mongo_io)])
            event.record_success()
            return event
        except ConfiguratorException as e:
            event.append_events([e.event])
            event.record_failure(f"ConfiguratorException processing configuration {self.file_name}")
            raise ConfiguratorException(f"ConfiguratorException processing configuration {self.file_name}", event)
        except Exception as e:
            event.record_failure(f"Unexpected error processing configuration {self.file_name}: {str(e)}")
            raise ConfiguratorException(f"Unexpected error processing configuration {self.file_name}: {str(e)}", event)

    @staticmethod
    def lock_all(status: bool = True):
        config = Config.get_instance()
        lock_all_event = ConfiguratorEvent(event_id="CFG-06", event_type="LOCK_ALL_CONFIGURATIONS", event_data={"status": status})
        try:
            for file in FileIO.get_documents(config.CONFIGURATION_FOLDER):
                file_event = ConfiguratorEvent(event_id=f"CFG-{file.file_name}", event_type="LOCK_CONFIGURATION")
                lock_all_event.append_events([file_event])
                configuration = Configuration(file.file_name)
                configuration._locked = status
                configuration.save()
                file_event.record_success()
            lock_all_event.record_success()
            return lock_all_event
        except ConfiguratorException as e:
            lock_all_event.append_events([e.event])
            file_event.record_failure(f"ConfiguratorException locking configuration {file.file_name}")
            lock_all_event.record_failure(f"ConfiguratorException locking configuration {file.file_name}")
            raise ConfiguratorException("Cannot lock all configurations", lock_all_event)
        except Exception as e:
            file_event.record_failure(f"Unexpected error locking configuration {file.file_name}")
            lock_all_event.record_failure(f"Unexpected error locking configuration {file.file_name}")
            raise ConfiguratorException("Cannot lock all configurations", lock_all_event)

    @staticmethod
    def process_all():
        config = Config.get_instance()
        process_event = ConfiguratorEvent("CFG-07", "PROCESS_ALL_CONFIGURATIONS")
        try:
            for file in FileIO.get_documents(config.CONFIGURATION_FOLDER):
                file_event = ConfiguratorEvent(f"CFG-{file.file_name}", "PROCESS_CONFIGURATION")
                file_event.append_events([Configuration(file.file_name).process()])
                file_event.record_success()
            process_event.record_success()
            return process_event
        except ConfiguratorException as e:
            file_event.record_failure(f"ConfiguratorException processing configuration {file.file_name}")
            process_event.append_events([e.event])
            process_event.record_failure(f"ConfiguratorException processing configuration {file.file_name}")
            raise ConfiguratorException("Cannot process all configurations", process_event)
        except Exception as e:
            file_event.record_failure(f"Unexpected error processing configuration {file.file_name}")
            process_event.record_failure(f"Unexpected error processing configuration {file.file_name}")
            raise ConfiguratorException("Cannot process all configurations", process_event)
                