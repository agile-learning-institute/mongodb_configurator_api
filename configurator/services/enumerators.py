from configurator.services.enumeration_service import Enumerations
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.utils.file_io import FileIO
from configurator.utils.config import Config
from configurator.utils.version_number import VersionNumber

class Enumerators:
    """A helper class for loading and accessing enumerations - not a service"""
    def __init__(self):
        self.config = Config.get_instance()
        self.enumerations = []

        files = FileIO.get_documents(self.config.ENUMERATOR_FOLDER)
        for file in files:
            self.enumerations.append(Enumerations(file.file_name))

    def get_version(self, version_str: str) -> Enumerations:
        """Get enumerations for a specific version string"""
        version_number = VersionNumber(version_str).get_enumerator_version()
        for enumeration in self.enumerations:
            if enumeration.version == version_number:
                return enumeration

        event = ConfiguratorEvent("ENU-06", "GET_ENUMERATION_VERSION")
        event.record_failure(f"Version {version_str} not found")
        raise ConfiguratorException(f"Version {version_str} not found", event)

