import os
os.environ['INPUT_FOLDER'] = './tests/test_cases/failing_refs'

from configurator.services.dictionary_services import Dictionary
from unittest.mock import Mock
from configurator.utils.configurator_exception import ConfiguratorException

mock_enumerations = Mock()
mock_enumerations.get_enum_values.return_value = []

try:
    dictionary = Dictionary('missing_type.1.0.0.yaml')
    dictionary.to_json_schema(mock_enumerations)
except ConfiguratorException as e:
    print(f'Exception: {e}')
    print(f'Event status: {e.event.status}')
    print(f'Event ID: {e.event.id}')
    print(f'Event type: {e.event.type}')
    print(f'Event data: {e.event.data}') 