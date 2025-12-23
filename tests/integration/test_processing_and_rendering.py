import os
import json
import unittest
from bson import json_util
from configurator.utils.version_number import VersionNumber
from configurator.utils.config import Config
from configurator.utils.mongo_io import MongoIO
from configurator.services.configuration_services import Configuration
from abc import ABC, abstractmethod
import datetime


def setup_test_environment(test_case, expected_pro_count):
    """Set up environment for a test case and return config."""
    # Set required environment variables
    os.environ['INPUT_FOLDER'] = f"./tests/test_cases/{test_case}"
    os.environ['ENABLE_DROP_DATABASE'] = 'true'
    os.environ['MONGODB_REQUIRE_TLS'] = 'false'
    # Note: MONGO_CONNECTION_STRING is not set here to allow it to use the default value
    # This is required for the drop_database safety check which requires connection string from "default"
    
    # Initialize config
    Config._instance = None
    config = Config.get_instance()
    
    # Clean up environment variables
    del os.environ['INPUT_FOLDER']
    del os.environ['ENABLE_DROP_DATABASE']
    del os.environ['MONGODB_REQUIRE_TLS']
    # MONGO_CONNECTION_STRING was not set, so no need to delete it
    
    return config, expected_pro_count


def drop_database(config):
    """Drop the database to ensure clean state."""
    mongo_io = MongoIO(config.MONGO_CONNECTION_STRING, config.MONGO_DB_NAME)
    mongo_io.drop_database()
    mongo_io.disconnect()


def load_verified_data(file_path):
    """Load verified output data from JSON file"""
    with open(file_path, 'r') as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)


def normalize_mongo_data(obj, collection_name=None):
    """Recursively convert MongoDB objects to string format for comparison"""
    if isinstance(obj, dict):
        return {k: normalize_mongo_data(v, collection_name) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_mongo_data(item, collection_name) for item in obj]
    elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'ObjectId':
        # For TestPassingTemplate, use MongoDB extended JSON format
        if collection_name == 'sample':
            return {"$oid": str(obj)}
        else:
            return str(obj)  # Convert ObjectId to string for other collections
    elif hasattr(obj, '__class__') and obj.__class__.__name__ in ['datetime', 'date']:
        return str(obj)  # Convert datetime/date to string
    else:
        return obj

def compare_database_data(actual_data, verified_data, collection_name=None):
    """Compare database data, handling 'ignore' values in verified output"""
    if isinstance(actual_data, dict) and isinstance(verified_data, dict):
        # Remove fields that are marked as 'ignore' in verified data
        # Also remove fields that exist in actual but not in verified
        filtered_actual = {}
        filtered_verified = {}
        
        for key, value in actual_data.items():
            if key in verified_data and verified_data[key] == 'ignore':
                continue  # Skip this field
            if key not in verified_data:
                continue  # Skip fields that don't exist in verified data
            # Skip _id field for system collections (ObjectIds are generated dynamically)
            if key == '_id' and (collection_name in ['DatabaseEnumerators', 'CollectionVersions'] or
                                verified_data.get('file_name', '').startswith('enumerations')):
                continue
            filtered_actual[key] = normalize_mongo_data(value, collection_name)
            
        for key, value in verified_data.items():
            if value == 'ignore':
                continue  # Skip this field
            # Skip _id field for system collections
            if key == '_id' and (collection_name in ['DatabaseEnumerators', 'CollectionVersions'] or
                                verified_data.get('file_name', '').startswith('enumerations')):
                continue
            filtered_verified[key] = value
            
        return filtered_actual == filtered_verified
    elif isinstance(actual_data, list) and isinstance(verified_data, list):
        if len(actual_data) != len(verified_data):
            return False
        
        # Sort both lists by version if they contain version fields
        if actual_data and isinstance(actual_data[0], dict) and 'version' in actual_data[0]:
            actual_data = sorted(actual_data, key=lambda x: x.get('version', 0))
        if verified_data and isinstance(verified_data[0], dict) and 'version' in verified_data[0]:
            verified_data = sorted(verified_data, key=lambda x: x.get('version', 0))
        
        for i, (actual, verified) in enumerate(zip(actual_data, verified_data)):
            if not compare_database_data(actual, verified, collection_name):
                print(f"List item {i} comparison failed:")
                print(f"  Actual: {actual}")
                print(f"  Verified: {verified}")
                return False
        return True
    else:
        return normalize_mongo_data(actual_data) == verified_data


class BaseProcessAndRenderTest(ABC):
    """Base class for processing and rendering tests"""
    
    @abstractmethod
    def setUp(self):
        """Set up test environment - must be implemented by subclasses"""
        pass
    
    @property
    @abstractmethod
    def test_case(self):
        """Test case name - must be implemented by subclasses"""
        pass
    
    @property
    @abstractmethod
    def expected_pro_count(self):
        """Expected number of processing events - must be implemented by subclasses"""
        pass

    @property
    @abstractmethod
    def expected_step_count(self):
        """Expected number of processing step events - must be implemented by subclasses"""
        pass

    def tearDown(self):
        Config._instance = None
        
    def count_processing_events(self, events):
        pro_count = 0
        step_count = 0
        if events:
            for event in events:
                if event.type == 'PROCESS':
                    pro_count += 1
                elif event.type == 'PROCESS_STEP':
                    step_count += 1
                
                if event.sub_events:
                    sub_pro_count, sub_step_count = self.count_processing_events(event.sub_events)
                    pro_count += sub_pro_count
                    step_count += sub_step_count
        return pro_count, step_count

    def test_process(self):
        """Test 1: Does processing produce expected events and match verified database?"""
        # Process configurations
        results = Configuration.process_all()
        
        # Save processing events to generated output
        generated_events_dir = f"{self.config.INPUT_FOLDER}/generated_output"
        os.makedirs(generated_events_dir, exist_ok=True)
        import yaml
        with open(f"{generated_events_dir}/processing_events.yaml", 'w') as f:
            yaml.dump(results.to_dict(), f, default_flow_style=False, sort_keys=False)
        
        # Verify processing succeeded
        self.assertEqual(results.status, "SUCCESS", f"Processing failed: {results.to_dict()}")
        
        pro_count, step_count = self.count_processing_events([results])        
        self.assertEqual(pro_count, self.expected_pro_count, f"Expected {self.expected_pro_count} successful processing events, found {pro_count}")
        self.assertEqual(step_count, self.expected_step_count, f"Expected {self.expected_step_count} successful processing step events, found {step_count}")
        
        # Compare database state with verified output
        verified_db_path = f"{self.config.INPUT_FOLDER}/verified_output/test_database"
        
        # Get expected collections from verified output files
        expected_collections = [f.replace('.json', '') for f in os.listdir(verified_db_path) if f.endswith('.json')]
        
        # Get actual collections from database
        actual_collections = self.mongo_io.db.list_collection_names()
        
        # Verify number of collections matches
        self.assertEqual(len(actual_collections), len(expected_collections),
                        f"Expected {len(expected_collections)} collections, found {len(actual_collections)}")
        
        # Compare each collection's data
        for filename in os.listdir(verified_db_path):
            if not filename.endswith('.json'):
                continue  # Skip non-JSON files like .gitkeep
            collection_name = filename.replace('.json', '')
            verified_data = load_verified_data(f"{verified_db_path}/{filename}")
            
            # Get actual database data
            actual_data = list(self.mongo_io.get_documents(collection_name))
            
            # Compare using the new comparison function
            self.assertTrue(compare_database_data(actual_data, verified_data, collection_name),
                            f"Database collection {collection_name} does not match verified output")

    def test_render_json(self):
        """Test 2: Do JSON schemas match verified output?"""
        verified_schema_dir = f"{self.config.INPUT_FOLDER}/verified_output/json_schema"
        generated_schema_dir = f"{self.config.INPUT_FOLDER}/generated_output/json_schema"
        
        # Create generated output directory if it doesn't exist
        os.makedirs(generated_schema_dir, exist_ok=True)
        
        for filename in os.listdir(verified_schema_dir):
            if filename.endswith('.yaml'):
                version_str = filename.replace('.yaml', '')
                verified_schema_path = f"{verified_schema_dir}/{filename}"
                generated_schema_path = f"{generated_schema_dir}/{filename}"
            
                # Load verified schema
                import yaml
                with open(verified_schema_path, 'r') as f:
                    expected_schema = yaml.safe_load(f)
            
                version_number = VersionNumber(version_str)
                collection_name = version_number.parts[0]
                configuration = Configuration(f"{collection_name}.yaml")
                actual_schema = configuration.get_json_schema(version_number.get_version_str())

                # Write generated schema to file
                with open(generated_schema_path, 'w') as f:
                    yaml.dump(actual_schema, f, default_flow_style=False, sort_keys=False)

                # Compare
                self.assertEqual(actual_schema, expected_schema,
                                f"JSON schema for {version_str} does not match verified output")

    def test_render_bson(self):
        """Test 3: Do BSON schemas match verified output?"""
        verified_schema_dir = f"{self.config.INPUT_FOLDER}/verified_output/bson_schema"
        generated_schema_dir = f"{self.config.INPUT_FOLDER}/generated_output/bson_schema"
        
        # Create generated output directory if it doesn't exist
        os.makedirs(generated_schema_dir, exist_ok=True)
        
        for filename in os.listdir(verified_schema_dir):
            if filename.endswith('.json'):
                version_str = filename.replace('.json', '')
                verified_schema_path = f"{verified_schema_dir}/{filename}"
                generated_schema_path = f"{generated_schema_dir}/{filename}"
                
                # Load verified schema
                expected_schema = load_verified_data(verified_schema_path)
                
                version_number = VersionNumber(version_str)
                collection_name = version_number.parts[0]
                configuration = Configuration(f"{collection_name}.yaml")
                actual_schema = configuration.get_bson_schema(version_number.get_version_str())
                actual_schema = normalize_mongo_data(actual_schema, collection_name)
                
                # Write generated schema to file
                with open(generated_schema_path, 'w') as f:
                    json.dump(actual_schema, f, indent=2, sort_keys=False)

                # Compare
                self.assertEqual(actual_schema, expected_schema,
                                f"BSON schema for {version_str} does not match verified output")

class TestPassingTemplate(BaseProcessAndRenderTest, unittest.TestCase):
    """Test passing_template test case"""
    
    @property
    def test_case(self):
        return "passing_template"
    
    @property
    def expected_pro_count(self):
        return 8
    
    @property
    def expected_step_count(self):
        return 13
    
    def setUp(self):
        self.config, _ = setup_test_environment(self.test_case, self.expected_pro_count)
        drop_database(self.config)
        self.mongo_io = MongoIO(self.config.MONGO_CONNECTION_STRING, self.config.MONGO_DB_NAME)


class TestPassingComplexRefs(BaseProcessAndRenderTest, unittest.TestCase):
    """Test passing_complex_refs test case"""
    
    @property
    def test_case(self):
        return "passing_complex_refs"
    
    @property
    def expected_pro_count(self):
        return 5
    
    @property
    def expected_step_count(self):
        return 4
    
    def setUp(self):
        self.config, _ = setup_test_environment(self.test_case, self.expected_pro_count)
        drop_database(self.config)
        self.mongo_io = MongoIO(self.config.MONGO_CONNECTION_STRING, self.config.MONGO_DB_NAME)


class TestPassingEmpty(BaseProcessAndRenderTest, unittest.TestCase):
    """Test passing_empty test case"""
    
    @property
    def test_case(self):
        return "passing_empty"
    
    @property
    def expected_pro_count(self):
        return 3
    
    @property
    def expected_step_count(self):
        return 0
    
    def setUp(self):
        self.config, _ = setup_test_environment(self.test_case, self.expected_pro_count)
        drop_database(self.config)
        self.mongo_io = MongoIO(self.config.MONGO_CONNECTION_STRING, self.config.MONGO_DB_NAME)


class TestPassingProcess(BaseProcessAndRenderTest, unittest.TestCase):
    """Test passing_process test case"""
    
    @property
    def test_case(self):
        return "passing_process"
    
    @property
    def expected_pro_count(self):
        return 22
    
    @property
    def expected_step_count(self):
        return 54
    
    def setUp(self):
        self.config, _ = setup_test_environment(self.test_case, self.expected_pro_count)
        drop_database(self.config)
        self.mongo_io = MongoIO(self.config.MONGO_CONNECTION_STRING, self.config.MONGO_DB_NAME) 

