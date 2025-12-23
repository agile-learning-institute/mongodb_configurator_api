from configurator.services.enumeration_service import Enumerations
from .base import BaseProperty
from configurator.services.dictionary_services import Dictionary
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException

class RefType(BaseProperty):
    def __init__(self, data: dict):
        super().__init__(data)
        self.ref = data.get("ref", "")

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict['ref'] = self.ref
        return the_dict

    def _get_dictionary_filename(self) -> str:
        """Get the dictionary filename, appending .yaml if no extension is present."""
        if self.ref.endswith('.yaml') or self.ref.endswith('.json'):
            return self.ref
        return f"{self.ref}.yaml"

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        try:
            dictionary_filename = self._get_dictionary_filename()
            dictionary = Dictionary(dictionary_filename)
            the_schema = dictionary.to_json_schema(enumerations, ref_stack)
            return the_schema
        except ConfiguratorException as e:
            # Wrap the exception with context about the ref property
            event = ConfiguratorEvent(event_id="REF-01", event_type="RENDER_REF_JSON_SCHEMA")
            event.data = {"ref": self.ref, "property_name": self.name}
            event.append_events([e.event])
            event.record_failure(f"Failed to render JSON schema for ref '{self.ref}' in property '{self.name}'")
            raise ConfiguratorException(f"Failed to render JSON schema for ref '{self.ref}' in property '{self.name}'", event)
        except Exception as e:
            event = ConfiguratorEvent(event_id="REF-01", event_type="RENDER_REF_JSON_SCHEMA")
            event.data = {"ref": self.ref, "property_name": self.name, "error": str(e)}
            event.record_failure(f"Unexpected error rendering JSON schema for ref '{self.ref}' in property '{self.name}': {str(e)}")
            raise ConfiguratorException(f"Unexpected error rendering JSON schema for ref '{self.ref}' in property '{self.name}': {str(e)}", event)

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        try:
            dictionary_filename = self._get_dictionary_filename()
            dictionary = Dictionary(dictionary_filename)
            the_schema = dictionary.to_bson_schema(enumerations, ref_stack)
            return the_schema
        except ConfiguratorException as e:
            # Wrap the exception with context about the ref property
            event = ConfiguratorEvent(event_id="REF-02", event_type="RENDER_REF_BSON_SCHEMA")
            event.data = {"ref": self.ref, "property_name": self.name}
            event.append_events([e.event])
            event.record_failure(f"Failed to render BSON schema for ref '{self.ref}' in property '{self.name}'")
            raise ConfiguratorException(f"Failed to render BSON schema for ref '{self.ref}' in property '{self.name}'", event)
        except Exception as e:
            event = ConfiguratorEvent(event_id="REF-02", event_type="RENDER_REF_BSON_SCHEMA")
            event.data = {"ref": self.ref, "property_name": self.name, "error": str(e)}
            event.record_failure(f"Unexpected error rendering BSON schema for ref '{self.ref}' in property '{self.name}': {str(e)}")
            raise ConfiguratorException(f"Unexpected error rendering BSON schema for ref '{self.ref}' in property '{self.name}': {str(e)}", event)

