import os
import yaml
from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.services.property import Property
from configurator.services.enumeration_service import Enumerations
from configurator.services.service_base import ServiceBase

class Type(ServiceBase):
    def __init__(self, file_name: str, document: dict = None):
        super().__init__(file_name, document, Config.get_instance().TYPE_FOLDER)
        self.root = Property(self._document.get("root", {}))

    def to_dict(self):
        d = super().to_dict()
        d["root"] = self.root.to_dict()
        return d

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        return self.root.to_json_schema(enumerations, ref_stack)

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        return self.root.to_bson_schema(enumerations, ref_stack)
    
    @staticmethod
    def lock_all(status: bool = True):
        return ServiceBase.lock_all(Type, Config.get_instance().TYPE_FOLDER, status)

