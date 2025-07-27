from flask import Blueprint, request, jsonify, abort, Response
from configurator.utils.config import Config
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.utils.file_io import FileIO, File
from configurator.utils.route_decorators import event_route
import json
import logging
import os
logger = logging.getLogger(__name__)

# Removed TestDataJSONEncoder as it's not being used and the global MongoJSONEncoder handles MongoDB objects

# Define the Blueprint for test_data routes
def create_test_data_routes():
    test_data_routes = Blueprint('test_data_routes', __name__)
    config = Config.get_instance()
    
    # GET /api/test_data - Return the current test_data files (only .json)
    @test_data_routes.route('/', methods=['GET'])
    @event_route("TST-01", "GET_TEST_DATA_FILES", "getting test data files")
    def get_data_files():
        files = FileIO.get_documents(config.TEST_DATA_FOLDER)
        return jsonify([file.to_dict() for file in files])
        
    # GET /api/test_data/<file_name> - Return a test_data file (only .json)
    @test_data_routes.route('/<file_name>/', methods=['GET'])
    @event_route("TST-02", "GET_TEST_DATA", "getting test data")
    def get_test_data(file_name):
        data = FileIO.get_document(config.TEST_DATA_FOLDER, file_name)
        return jsonify(data)
    
    # PUT /api/test_data/<file_name> - Update a test_data file (only .json)
    @test_data_routes.route('/<file_name>/', methods=['PUT'])
    @event_route("TST-03", "PUT_TEST_DATA", "updating test data")
    def update_test_data(file_name):
        data = FileIO.put_document(config.TEST_DATA_FOLDER, file_name, request.json)
        return jsonify(data)
        
    @test_data_routes.route('/<file_name>/', methods=['DELETE'])
    @event_route("TST-04", "DELETE_TEST_DATA", "deleting test data")
    def delete_test_data(file_name):
        event = FileIO.delete_document(config.TEST_DATA_FOLDER, file_name)
        return jsonify(event.to_dict())
        
    logger.info("test_data Flask Routes Registered")
    return test_data_routes