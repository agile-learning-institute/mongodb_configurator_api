import os
os.environ['INPUT_FOLDER'] = './tests/test_cases/failing_refs'

from configurator.services.configuration_services import Configuration
from configurator.utils.configurator_exception import ConfiguratorException

try:
    configuration = Configuration("test_data.yaml")
    configuration.get_json_schema("1.0.0.0")
except ConfiguratorException as e:
    print(f'Exception: {e}')
    print(f'Event status: {e.event.status}')
    print(f'Event ID: {e.event.id}')
    print(f'Event type: {e.event.type}')
    print(f'Event data: {e.event.data}') 