from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.mongo_io import MongoIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.services.configuration_version import Version
from configurator.services.enumerators import Enumerators
from configurator.services.service_base import ServiceBase

import logging
logger = logging.getLogger(__name__)

class Configuration(ServiceBase):
    def __init__(self, file_name: str = None, document: dict = None):
        super().__init__(file_name, document, Config.get_instance().CONFIGURATION_FOLDER)
        self.collection_name = self.file_name.split('.')[0]
        self.title = self._document.get("title", "")
        self.description = self._document.get("description", "")
        self.versions = [Version(self.collection_name, v) for v in self._document.get("versions", [])]

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict["title"] = self.title
        the_dict["description"] = self.description
        the_dict["versions"] = [v.to_dict() for v in self.versions]
        return the_dict

    def get_version(self, version_str: str) -> Version:
        for version in self.versions:
            if version.version_str == version_str:
                return version
            
        event = ConfiguratorEvent("CFG-02", "GET_JSON_SCHEMA")
        event.record_failure(f"Version {version_str} not found in configuration {self.file_name}")
        logger.error(f"Version {version_str} not found in configuration {self.file_name}")
        raise ConfiguratorException(f"Version {version_str} not found in configuration {self.file_name}", event)

    def get_json_schema(self, version_str: str) -> dict:
        version = self.get_version(version_str)
        enumerators = Enumerators()
        enumerations = enumerators.get_version(f"{self.collection_name}.{version_str}")
        return version.get_json_schema(enumerations)

    def get_bson_schema(self, version_str: str) -> dict:
        version = self.get_version(version_str)
        enumerators = Enumerators()
        enumerations = enumerators.get_version(f"{self.collection_name}.{version_str}")
        return version.get_bson_schema(enumerations)
        
    def process(self, mongo_io: MongoIO) -> ConfiguratorEvent:
        event = ConfiguratorEvent(event_id=f"CFG-05-{self.file_name}", event_type="PROCESS")
        event.data = {"configuration_name": self.file_name, "version_count": len(self.versions)}
        try:
            for version in self.versions:
                event.append_events([version.process(mongo_io)])
            event.record_success()
            return event
        except ConfiguratorException as e:
            event.record_failure(f"ConfiguratorException processing configuration {self.file_name}")
            event.append_events([e.event])
            logger.error(f"ConfiguratorException processing configuration {self.file_name}: {e.event.to_dict()}")
            raise ConfiguratorException(f"ConfiguratorException processing configuration {self.file_name}", event)
        except Exception as e:
            event.record_failure(f"Unexpected error processing configuration {self.file_name}: {str(e)}")
            logger.error(f"Unexpected error processing configuration {self.file_name}: {str(e)}")
            raise ConfiguratorException(f"Unexpected error processing configuration {self.file_name}: {str(e)}", event)

    @staticmethod
    def lock_all(status: bool = True):
        return ServiceBase.lock_all(Configuration, Config.get_instance().CONFIGURATION_FOLDER, status)

    @staticmethod
    def update_enumerators(mongo_io: MongoIO) -> ConfiguratorEvent:
        event = ConfiguratorEvent("CFG-06-UPDATE_ENUMERATORS", "PROCESS")
        try:
            enumerators = Enumerators()
            for enumeration in enumerators.enumerations:
                logger.info(f"Updating enumeration {enumeration.file_name}")
                event.append_events([enumeration.upsert(mongo_io)])
            event.record_success()
            return event
        except ConfiguratorException as e:
            event.append_events([e.event])
            event.record_failure(f"ConfiguratorException updating enumerators")
            logger.error(f"ConfiguratorException updating enumerators - {e.event.to_dict()}")
            raise ConfiguratorException("Cannot update enumerators", event)
        except Exception as e:
            event.record_failure(f"Unexpected error updating enumerators: {str(e)}")
            logger.error(f"Unexpected error updating enumerators: {str(e)}")
            raise ConfiguratorException("Cannot update enumerators", event)

    @staticmethod
    def process_all():
        config = Config.get_instance()
        process_event = ConfiguratorEvent("CFG-07-PROCESS_ALL", "PROCESS")

        # Update enumerators
        try:
            mongo_io = MongoIO(config.MONGO_CONNECTION_STRING, config.MONGO_DB_NAME)
            process_event.append_events([Configuration.update_enumerators(mongo_io)])
        except ConfiguratorException as e:
            process_event.append_events([e.event])
            process_event.record_failure(f"ConfiguratorException updating enumerators")
            logger.error(f"ConfiguratorException updating enumerators - {e.event.to_dict()}")
            return process_event
        except Exception as e:
            process_event.record_failure(f"Unexpected error updating enumerators: {str(e)}")
            logger.error(f"Unexpected error updating enumerators: {str(e)}")
            return process_event
        
        # Process configuration files
        for file in FileIO.get_documents(config.CONFIGURATION_FOLDER):
            try:
                process_event.append_events([Configuration(file.file_name).process(mongo_io)])
            except ConfiguratorException as e:
                process_event.append_events([e.event])
                process_event.record_failure(f"ConfiguratorException processing configuration {file.file_name}")
                logger.error(f"ConfiguratorException processing configuration {file.file_name}: {e.event.to_dict()}")
            except Exception as e:
                process_event.append_events([e.event])
                process_event.record_failure(f"Unexpected error {str(e)} processing configuration {file.file_name}")
                logger.error(f"Unexpected error {str(e)} processing configuration {file.file_name}: {e.event.to_dict()}")
        process_event.record_success()
        return process_event
                        
    @staticmethod
    def process_one(file_name: str):
        config = Config.get_instance()
        process_event = ConfiguratorEvent("CFG-09-PROCESS_ONE_CONFIGURATION", "PROCESS")
            
        try:
            mongo_io = MongoIO(config.MONGO_CONNECTION_STRING, config.MONGO_DB_NAME)
            process_event.append_events([Configuration.update_enumerators(mongo_io)])
            process_event.append_events([Configuration(file_name).process(mongo_io)])
            process_event.record_success()
            return process_event
        except ConfiguratorException as e:
            process_event.record_failure(f"ConfiguratorException processing configuration {file_name}")
            process_event.append_events([e.event])
            logger.error(f"ConfiguratorException processing configuration {file_name}: {e.event.to_dict()}")
            return process_event
        except Exception as e:
            process_event.record_failure(f"Unexpected error {str(e)} processing configuration {file_name}")
            logger.error(f"Unexpected error {str(e)} processing configuration {file_name}: {process_event.to_dict()}")
            return process_event
                                