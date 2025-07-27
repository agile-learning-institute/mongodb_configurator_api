from flask import Blueprint, request, jsonify
from configurator.utils.config import Config
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.utils.file_io import FileIO
from configurator.services.dictionary_services import Dictionary
from configurator.utils.route_decorators import event_route
import logging
logger = logging.getLogger(__name__)

# Define the Blueprint for dictionary routes
def create_dictionary_routes():
    dictionary_routes = Blueprint('dictionary_routes', __name__)
    config = Config.get_instance()
    
    # GET /api/dictionaries - Return the current dictionary files
    @dictionary_routes.route('/', methods=['GET'])
    @event_route("DIC-01", "GET_DICTIONARIES", "listing dictionaries")
    def get_dictionaries():
        files = FileIO.get_documents(config.DICTIONARY_FOLDER)
        return jsonify([file.to_dict() for file in files])
    
    # PATCH /api/dictionaries/ - Lock All Dictionaries
    @dictionary_routes.route('/', methods=['PATCH'])
    @event_route("DIC-04", "LOCK_ALL_DICTIONARIES", "locking all dictionaries")
    def lock_all_dictionaries():
        result = Dictionary.lock_all()
        return jsonify(result.to_dict())
    
    # GET /api/dictionaries/<file_name> - Return a dictionary file
    @dictionary_routes.route('/<file_name>/', methods=['GET'])
    @event_route("DIC-02", "GET_DICTIONARY", "getting dictionary")
    def get_dictionary(file_name):
        dictionary = Dictionary(file_name)
        return jsonify(dictionary.to_dict())
    
    # PUT /api/dictionaries/<file_name> - Update a dictionary file
    @dictionary_routes.route('/<file_name>/', methods=['PUT'])
    @event_route("DIC-03", "PUT_DICTIONARY", "updating dictionary")
    def update_dictionary(file_name):
        dictionary = Dictionary(file_name, request.json)
        result = dictionary.save()
        return jsonify(result)
    
    @dictionary_routes.route('/<file_name>/', methods=['DELETE'])
    @event_route("DIC-05", "DELETE_DICTIONARY", "deleting dictionary")
    def delete_dictionary(file_name):
        dictionary = Dictionary(file_name)
        event = dictionary.delete()
        return jsonify(event.to_dict())
    
    logger.info("dictionary Flask Routes Registered")
    return dictionary_routes