import json
from bson import ObjectId 
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.operations import IndexModel
from bson import json_util
from configurator.utils.config import Config
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException

import logging
import os
from pymongo.errors import BulkWriteError

logger = logging.getLogger(__name__)

class MongoIO:
    """Simplified MongoDB I/O class for configuration services."""

    def __init__(self, connection_string, database_name):
        try:
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=2000, 
                socketTimeoutMS=5000
            )
            self.client.admin.command('ping')  # Force connection
            self.db = self.client.get_database(database_name)
            logger.info(f"Connected to MongoDB: {database_name}")
        except Exception as e:
            event = ConfiguratorEvent(event_id="MON-01", event_type="CONNECTION", event_data={"error": str(e)})
            raise ConfiguratorException("Failed to connect to MongoDB", event)

    def disconnect(self):
        try:
            if self.client:
                self.client.close()
                self.client = None
                logger.info("Disconnected from MongoDB")
        except Exception as e:
            # Log the error but don't raise it - disconnect should be safe to call
            logger.warning(f"Error during disconnect: {e}")
            # Clear the client reference even if close failed
            self.client = None

    def get_collection(self, collection_name):
        """Get a collection, creating it if it doesn't exist."""
        try:
            if collection_name not in self.db.list_collection_names():
                self.db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
            
            return self.db.get_collection(collection_name)
        except Exception as e:
            event = ConfiguratorEvent(event_id="MON-03", event_type="COLLECTION", event_data={"error": str(e), "collection": collection_name})
            raise ConfiguratorException(f"Failed to get/create collection {collection_name}", event)
      
    def get_documents(self, collection_name, match=None, project=None, sort_by=None):        
        try:
            match = match or {}
            project = project or None
            sort_by = sort_by or None
            collection = self.get_collection(collection_name)
            cursor = collection.find(match, project)
            if sort_by: 
                cursor = cursor.sort(sort_by)

            documents = list(cursor)
            return documents
        except Exception as e:
            event = ConfiguratorEvent(event_id="MON-04", event_type="GET_DOCUMENTS", event_data={"error": str(e), "collection": collection_name})
            raise ConfiguratorException(f"Failed to get documents from {collection_name}", event)
                
    def upsert(self, collection_name, match, data):
        try:
            collection = self.get_collection(collection_name)
            result = collection.find_one_and_update(
                match,
                {"$set": data},
                upsert=True,
                return_document=True
            )
            return result
        except Exception as e:
            event = ConfiguratorEvent(event_id="MON-05", event_type="UPSERT", event_data={"error": str(e), "collection": collection_name})
            raise ConfiguratorException(f"Failed to upsert document in {collection_name}", event)

    def remove_schema_validation(self, collection_name):
        try:
            event = ConfiguratorEvent(event_id="MON-06", event_type="REMOVE_SCHEMA")
            self.get_collection(collection_name)
            
            command = {
                "collMod": collection_name,
                "validator": {}
            }
            
            result = self.db.command(command)
            logger.info(f"Schema validation cleared successfully: {collection_name}")
            event.data = {
                "collection": collection_name,
                "operation": "schema_validation_removed"
            }
            event.record_success()
            return [event]
        except Exception as e:
            event.record_failure({"error": str(e), "collection": collection_name})
            raise ConfiguratorException(f"Failed to remove schema validation from {collection_name}", event)

    def remove_index(self, collection_name, index_name):    
        try:
            event = ConfiguratorEvent(event_id="MON-07", event_type="REMOVE_INDEX")
            collection = self.get_collection(collection_name)
            collection.drop_index(index_name)
            logger.info(f"Dropped index {index_name} from collection: {collection_name}")
            event.data = {
                "collection": collection_name,
                "index_name": index_name,
                "operation": "dropped"
            }
            event.record_success()
            return [event]
        except Exception as e:
            event.record_failure({"error": str(e), "collection": collection_name, "index": index_name})
            raise ConfiguratorException(f"Failed to remove index {index_name} from {collection_name}", event)

    def execute_migration(self, collection_name, pipeline):    
        try:
            event = ConfiguratorEvent(event_id="MON-08", event_type="EXECUTE_MIGRATION", event_data={"collection": collection_name})
            collection = self.get_collection(collection_name)
            result = list(collection.aggregate(pipeline))
            logger.info(f"Executed migration on collection: {collection_name}")
            event.record_success()
            return [event]
        except Exception as e:
            event.record_failure({"error": str(e), "collection": collection_name})
            raise ConfiguratorException(f"Failed to execute migration on {collection_name}", event)

    def load_migration_pipeline(self, migration_file):
        try:
            with open(migration_file, 'r') as file:
                # Use bson.json_util.loads to preserve $ prefixes in MongoDB operators
                pipeline = json_util.loads(file.read())
            logger.info(f"Loaded migration pipeline from: {migration_file}")
            return pipeline
        except Exception as e:
            event = ConfiguratorEvent(event_id="MON-13", event_type="LOAD_MIGRATION")
            event.record_failure({"error": str(e), "file": migration_file})
            raise ConfiguratorException(f"Failed to load migration pipeline from {migration_file}", event)

    def execute_migration_from_file(self, collection_name, migration_file):
        event = ConfiguratorEvent(event_id="MON-14", event_type="EXECUTE_MIGRATION_FILE")
        event.data = {
            "collection": collection_name,
            "migration_file": os.path.basename(migration_file)
        }
        
        try:
            sub_event = ConfiguratorEvent(event_id="MON-13", event_type="LOAD_MIGRATION")
            event.append_events([sub_event])
            pipeline = self.load_migration_pipeline(migration_file)
            sub_event.record_success()
            
            sub_event = ConfiguratorEvent(event_id="MON-08", event_type="EXECUTE_MIGRATION")
            event.append_events([sub_event])
            self.execute_migration(collection_name, pipeline)
            sub_event.record_success()
            return [event]
        except Exception as e:
            event.record_failure({"error": str(e), "collection": collection_name, "file": migration_file})
            return [event]

    def add_index(self, collection_name, index_spec):
        try:
            event = ConfiguratorEvent(event_id="MON-09", event_type="ADD_INDEX")
            collection = self.get_collection(collection_name)
            index_model = IndexModel(index_spec["key"], name=index_spec["name"])
            collection.create_indexes([index_model])
            logger.info(f"Created index {index_spec['name']} on collection: {collection_name}")
            event.data = {
                "collection": collection_name,
                "index_name": index_spec["name"],
                "index_keys": index_spec["key"],
                "operation": "created"
            }
            event.record_success()
            return [event]
        except Exception as e:
            event.record_failure({"error": str(e), "collection": collection_name, "index": index_spec})
            raise ConfiguratorException(f"Failed to add index {index_spec['name']} to {collection_name}", event)

    def apply_schema_validation(self, collection_name, schema_dict):
        try:
            event = ConfiguratorEvent(event_id="MON-10", event_type="APPLY_SCHEMA")
            # Apply schema validation to MongoDB collection
            collection = self.get_collection(collection_name)
            command = {
                "collMod": collection_name,
                "validator": {"$jsonSchema": schema_dict},
                "validationLevel": "moderate",
                "validationAction": "error"
            }
            
            result = self.db.command(command)
            logger.info(f"Schema validation applied to collection: {collection_name}")
            event.data = schema_dict
            event.record_success()
            return [event]
            
        except Exception as e:
            event.record_failure({"error": str(e), "collection": collection_name})
            return [event]

    def load_json_data(self, collection_name, data_file):
        event = ConfiguratorEvent(event_id="MON-11", event_type="LOAD_DATA")
        
        try:
            collection = self.get_collection(collection_name)
            with open(data_file, 'r') as file:
                from bson import json_util
                data = json_util.loads(file.read())
            
            logger.info(f"Loading {len(data)} documents from {data_file} into collection: {collection_name}")
            result = collection.insert_many(data)
            
            event.data = {
                "collection": collection_name,
                "data_file": os.path.basename(data_file),
                "documents_loaded": len(data),
                "insert_many_result": {
                    "inserted_ids": [str(oid) for oid in result.inserted_ids],
                    "acknowledged": result.acknowledged
                }
            }
            event.record_success()
            return [event]
        except BulkWriteError as e:
            event.record_failure("Bulk write operation failed", e.details)
            raise ConfiguratorException(f"Bulk write operation failed: {e.details}", event)
        except Exception as e:
            event.record_failure("Bulk write operation failed unexpectedly", {"error": str(e)})
            raise ConfiguratorException(f"Bulk write operation failed unexpectedly: {e}, {collection_name}, {data_file}", event)

    def drop_database(self) -> list[ConfiguratorEvent]:
        config = Config.get_instance()
        event = ConfiguratorEvent(event_id="MON-12", event_type="DROP_DATABASE")

        if not config.ENABLE_DROP_DATABASE:
            event.record_failure({"error": "Drop database feature is not enabled"})
            raise ConfiguratorException("Drop database feature is not enabled", event)

        if not config.BUILT_AT == "Local":
            event.record_failure({"error": "Drop database not allowed on Non-Local Build"})
            raise ConfiguratorException("Drop database not allowed on Non-Local Build", event)
        
        # Check if any collections have more than 100 documents
        try:
            collections_with_many_docs = []
            for collection_name in self.db.list_collection_names():
                sub_event = ConfiguratorEvent(event_id=f"MON-{collection_name}", event_type="COUNT_DOCUMENTS")
                doc_count = self.db.get_collection(collection_name).count_documents({})
                if doc_count > 100:
                    collections_with_many_docs.append({
                        "collection": collection_name,
                        "document_count": doc_count
                    })
                sub_event.record_success()
                event.append_events([sub_event])
            
            if collections_with_many_docs:
                event.event_data = collections_with_many_docs
                event.record_failure("Drop database Safety Limit Exceeded - Collections with >100 documents found")
                raise ConfiguratorException("Drop database Safety Limit Exceeded - Collections with >100 documents found", event)
            
            self.client.drop_database(self.db.name)
            event.record_success()
            logger.info(f"Dropped database: {self.db.name}")
            return [event]
        except Exception as e:
            event.event_data = e
            event.record_failure("Check collection counts raised an exception")
            raise ConfiguratorException("Check collection counts raised an exception", event)
