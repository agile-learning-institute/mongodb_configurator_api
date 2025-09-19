import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile
import json

from configurator.services.configuration_services import Configuration, Version
from configurator.utils.mongo_io import MongoIO
from configurator.utils.config import Config


class TestMigrationEvents(unittest.TestCase):
    """Test migration event functionality with simplified, robust tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config.get_instance()
        self.config.INPUT_FOLDER = tempfile.mkdtemp()
        
        # Create a test migration file
        self.migration_file = os.path.join(self.config.INPUT_FOLDER, "migrations", "test_migration.json")
        os.makedirs(os.path.dirname(self.migration_file), exist_ok=True)
        
        # Create a simple migration pipeline
        migration_pipeline = [
            {"$addFields": {"test_field": "test_value"}},
            {"$out": "test_collection"}
        ]
        
        with open(self.migration_file, 'w') as f:
            json.dump(migration_pipeline, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.config.INPUT_FOLDER)
    
    @patch('configurator.utils.mongo_io.MongoClient')
    @patch('configurator.services.configuration_version.Enumerators')
    def test_migration_events_created_successfully(self, mock_enumerators, mock_client):
        """Test that migration events are created with SUCCESS status."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.aggregate.return_value = []
        
        # Mock the admin command for ping
        mock_admin = MagicMock()
        mock_client_instance.admin = mock_admin
        mock_admin.command.return_value = {"ok": 1}
        
        # Patch Enumerators.version to return a dummy enumerations object
        mock_enumerators.return_value.version.return_value = {}
        
        # Create a configuration with migrations
        config_data = {
            "title": "Test Collection",
            "description": "Test collection for migration events",
            "name": "test_collection",
            "versions": [
                {
                    "version": "1.0.0.1",
                    "migrations": ["test_migration.json"]
                }
            ]
        }
        
        # Create configuration and version objects
        config = Configuration("test.yaml", config_data)
        version = config.versions[0]
        
        # Patch get_bson_schema to return a minimal valid schema
        version.get_bson_schema = MagicMock(return_value={"type": "object", "properties": {}})
        
        # Mock MongoIO
        mongo_io = MongoIO("mongodb://localhost:27017", "test_db")
        
        # Process the version
        event = version.process(mongo_io)
        
        # Verify the main event structure
        self.assertEqual(event.status, "SUCCESS")
        self.assertIsNotNone(event.sub_events)
        
        # Check that we have migration-related events (without being too specific about structure)
        event_ids = [sub_event.id for sub_event in event.sub_events]
        migration_events = [event_id for event_id in event_ids if "MIGRATION" in event_id or "migration" in event_id]
        
        # Should have at least one migration-related event
        self.assertGreater(len(migration_events), 0, "Should have migration-related events")
        
        # All migration events should be successful
        for sub_event in event.sub_events:
            if "MIGRATION" in sub_event.id or "migration" in sub_event.id:
                self.assertEqual(sub_event.status, "SUCCESS", f"Migration event {sub_event.id} should be successful")
    
    def test_migration_file_loading(self):
        """Test that migration files can be loaded correctly."""
        # Test that the migration file exists and can be loaded
        self.assertTrue(os.path.exists(self.migration_file))
        
        with open(self.migration_file, 'r') as f:
            migration_data = json.load(f)
        
        # Verify the migration data structure
        self.assertIsInstance(migration_data, list)
        self.assertGreater(len(migration_data), 0)
        
        # Check that it contains expected MongoDB aggregation pipeline stages
        self.assertIn("$addFields", migration_data[0])
        self.assertIn("$out", migration_data[1])


if __name__ == '__main__':
    unittest.main() 