from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.mongo_io import MongoIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.services.configuration_version import Version
from configurator.services.enumerator_service import Enumerators
from configurator.services.service_base import ServiceBase

class Configuration(ServiceBase):
    def __init__(self, file_name: str = None, document: dict = None):
        super().__init__(file_name, document, "configurations")
        self.collection_name = self.file_name.split('.')[0]
        self.title = self._document.get("title", "")
        self.description = self._document.get("description", "")
        self.versions = [Version(self.collection_name, v) for v in self._document.get("versions", [])]

    def to_dict(self):
        d = super().to_dict()
        d["title"] = self.title
        d["description"] = self.description
        d["versions"] = [v.to_dict() for v in self.versions]
        return d

    @staticmethod
    def _get_folder_name():
        return "configurations"

    def get_json_schema(self, version_str: str) -> dict:
        for version in self.versions:
            if version.version_str == version_str:
                enumerations = Enumerators().getVersion(version.version_number.get_enumerator_version())
                return version.get_json_schema(enumerations)
        
        event = ConfiguratorEvent("CFG-02", "GET_JSON_SCHEMA")
        event.record_failure(f"Version {version_str} not found")
        raise ConfiguratorException(f"Version {version_str} not found", event)

    def get_bson_schema(self, version_str: str) -> dict:
        """Get BSON schema for a specific version."""
        for version in self.versions:
            if version.version_str == version_str:
                enumerations = Enumerators().getVersion(version.version_number.get_enumerator_version())
                return version.get_bson_schema(enumerations)
        
        event = ConfiguratorEvent("CFG-03", "GET_BSON_SCHEMA")
        event.record_failure(f"Version {version_str} not found")
        raise ConfiguratorException(f"Version {version_str} not found", event)
        
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
        return ServiceBase.lock_all(Configuration, status)

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
                