import os
from configurator.services.dictionary_services import Dictionary
from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.mongo_io import MongoIO
from configurator.utils.version_number import VersionNumber
from configurator.utils.version_manager import VersionManager
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.services.enumeration_service import Enumerations
from configurator.services.enumerators import Enumerators

class Version:
    def __init__(self, collection_name: str, document: dict):
        self.config = Config.get_instance()
        self.collection_name = collection_name        
        self.version_number = VersionNumber(f"{collection_name}.{document['version']}")
        self.version_str = self.version_number.get_version_str()
        self.drop_indexes = document.get("drop_indexes", [])
        self.add_indexes = document.get("add_indexes", [])
        self.migrations = document.get("migrations", [])
        self.test_data = document.get("test_data", None)
        self._locked = document.get("_locked", False)

    def to_dict(self):
        the_dict = {}
        the_dict["version"] = self.version_number.get_version_str()
        the_dict["drop_indexes"] = self.drop_indexes
        the_dict["add_indexes"] = self.add_indexes
        the_dict["migrations"] = self.migrations
        the_dict["test_data"] = self.test_data
        the_dict["_locked"] = self._locked
        return the_dict

    def get_json_schema(self, enumerations: Enumerations) -> dict:
        dictionary_filename: str = self.version_number.get_schema_filename()
        dictionary = Dictionary(dictionary_filename)
        return dictionary.to_json_schema(enumerations)

    def get_bson_schema(self, enumerations: Enumerations) -> dict:
        dictionary_filename: str = self.version_number.get_schema_filename()
        dictionary = Dictionary(dictionary_filename)
        return dictionary.to_bson_schema(enumerations)

    def process(self, mongo_io: MongoIO) -> ConfiguratorEvent:
        try:
            event = ConfiguratorEvent(event_id=f"{self.collection_name}.{self.version_str}", event_type="PROCESS")
            
            # If current version is greater than or equal to this version, skip processing
            current_version = VersionManager.get_current_version(mongo_io, self.collection_name)
            if current_version >= self.version_number:
                event.data = {
                    "skip_reason": "Version already implemented",
                    "current_version": str(current_version),
                    "target_version": self.version_number.get_version_str()
                }
                event.record_success()
                return event
            
            # Remove schema validation
            sub_event = ConfiguratorEvent(event_id="PRO-01", event_type="REMOVE_SCHEMA_VALIDATION")
            event.append_events([sub_event])
            sub_event.append_events(mongo_io.remove_schema_validation(self.collection_name))
            sub_event.record_success()

            # Remove indexes
            if self.drop_indexes:
                sub_event = ConfiguratorEvent(event_id="PRO-02", event_type="REMOVE_INDEXES")
                event.append_events([sub_event])
                for index_name in self.drop_indexes:
                    sub_event.append_events(mongo_io.remove_index(self.collection_name, index_name))                    
                sub_event.record_success()

            # Execute migrations
            if self.migrations:
                sub_event = ConfiguratorEvent(event_id="PRO-03", event_type="EXECUTE_MIGRATIONS")
                event.append_events([sub_event])
                for filename in self.migrations:
                    migration_file = os.path.join(self.config.INPUT_FOLDER, self.config.MIGRATIONS_FOLDER, filename)
                    sub_event.append_events(mongo_io.execute_migration_from_file(self.collection_name, migration_file))
                    sub_event.record_success()

            # Add indexes
            if self.add_indexes:
                sub_event = ConfiguratorEvent(event_id="PRO-04", event_type="ADD_INDEXES")
                event.append_events([sub_event])
                for index in self.add_indexes:
                    sub_event.append_events(mongo_io.add_index(self.collection_name, index))
                sub_event.record_success()

            # Apply schema validation
            sub_event = ConfiguratorEvent(event_id="PRO-06", event_type="APPLY_SCHEMA_VALIDATION")
            event.append_events([sub_event])
            enumerations = Enumerators().get_version(self.version_str)
            bson_schema: dict = self.get_bson_schema(enumerations)
            
            # Add schema context to event
            sub_event.append_events(mongo_io.apply_schema_validation(self.collection_name, bson_schema))
            sub_event.record_success()

            # Load test data
            if self.test_data:
                sub_event = ConfiguratorEvent(event_id="PRO-07", event_type="LOAD_TEST_DATA")
                event.append_events([sub_event])
                test_data_path = os.path.join(self.config.INPUT_FOLDER, self.config.TEST_DATA_FOLDER, self.test_data)
                sub_event.data = {"test_data_path": test_data_path}
                sub_event.append_events(mongo_io.load_json_data(self.collection_name, test_data_path))
                sub_event.record_success()

            # Update version
            sub_event = ConfiguratorEvent(event_id="PRO-08", event_type="UPDATE_VERSION")
            event.append_events([sub_event])
            result = mongo_io.upsert(
                self.config.VERSION_COLLECTION_NAME,
                {"collection_name": self.collection_name},
                {"collection_name": self.collection_name, "current_version": self.version_number.version}
            )
            sub_event.data = result
            sub_event.record_success()

            event.record_success()
            return event
        
        except ConfiguratorException as e:
            sub_event.record_failure(f"ConfiguratorException processing version {self.version_str}: {str(e)}")
            event.append_events([e.event])
            event.record_failure(f"ConfiguratorException processing version {self.version_str}: {str(e)}")
            raise ConfiguratorException(f"ConfiguratorException processing version {self.version_str}: {str(e)}", event)
        except Exception as e:
            sub_event.record_failure(f"Unexpected error processing version {self.version_str}: {str(e)}")
            event.record_failure(f"Unexpected error processing version {self.version_str}: {str(e)}")
            raise ConfiguratorException(f"Unexpected error processing version {self.version_str}: {str(e)}", event)
