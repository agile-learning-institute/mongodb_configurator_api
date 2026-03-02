import unittest
import os
from unittest.mock import patch, Mock
from flask import Flask
from configurator.routes.collection_routes import create_collection_routes
from configurator.utils.config import Config


class TestCollectionRoutes(unittest.TestCase):
    """Test cases for collection routes."""

    def setUp(self):
        """Set up test fixtures."""
        Config._instance = None
        self._original_input_folder = os.environ.get('INPUT_FOLDER')
        if 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']

        self.app = Flask(__name__)
        self.app.register_blueprint(create_collection_routes(), url_prefix='/api/collections')
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after tests."""
        if self._original_input_folder:
            os.environ['INPUT_FOLDER'] = self._original_input_folder
        elif 'INPUT_FOLDER' in os.environ:
            del os.environ['INPUT_FOLDER']
        Config._instance = None

    @patch('configurator.routes.collection_routes.Configuration')
    def test_get_collections_success(self, mock_configuration_class):
        """Test successful GET /api/collections/."""
        mock_configuration_class.get_collections_summary.return_value = [
            {
                "collection_name": "sample",
                "configuration_file": "sample.yaml",
                "latest_dictionary_file": "sample.1.0.0.yaml",
                "latest_version": "1.0.0.0",
                "_locked": False,
            }
        ]

        response = self.client.get('/api/collections/')

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["collection_name"], "sample")
        self.assertEqual(data[0]["configuration_file"], "sample.yaml")
        self.assertEqual(data[0]["latest_dictionary_file"], "sample.1.0.0.yaml")
        self.assertEqual(data[0]["latest_version"], "1.0.0.0")
        self.assertFalse(data[0]["_locked"])

    @patch('configurator.routes.collection_routes.Configuration')
    def test_get_collections_empty(self, mock_configuration_class):
        """Test GET /api/collections/ when no collections exist."""
        mock_configuration_class.get_collections_summary.return_value = []

        response = self.client.get('/api/collections/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    @patch('configurator.routes.collection_routes.Configuration')
    def test_get_collections_general_exception(self, mock_configuration_class):
        """Test GET /api/collections/ when Configuration raises exception."""
        mock_configuration_class.get_collections_summary.side_effect = Exception("Unexpected error")

        response = self.client.get('/api/collections/')

        self.assertEqual(response.status_code, 500)
        data = response.json
        self.assertIn("status", data)
        self.assertEqual(data["status"], "FAILURE")


if __name__ == '__main__':
    unittest.main()
