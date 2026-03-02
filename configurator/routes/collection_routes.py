from flask import Blueprint, jsonify
from configurator.services.configuration_services import Configuration
from configurator.utils.route_decorators import event_route
import logging


logger = logging.getLogger(__name__)


def create_collection_routes():
    blueprint = Blueprint('collections', __name__)

    @blueprint.route('/', methods=['GET'])
    @event_route("COL-01", "GET_COLLECTIONS", "listing collections")
    def get_collections():
        summaries = Configuration.get_collections_summary()
        return jsonify(summaries)

    logger.info("collection Flask Routes Registered")
    return blueprint
