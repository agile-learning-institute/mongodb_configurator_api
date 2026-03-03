import os
import yaml
import logging
from configurator.utils.config import Config
from configurator.utils.file_io import FileIO
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException
from configurator.services.property import Property
from configurator.services.enumeration_service import Enumerations
from configurator.services.service_base import ServiceBase

logger = logging.getLogger(__name__)


class Type(ServiceBase):
    def __init__(self, file_name: str, document: dict = None):
        super().__init__(file_name, document, Config.get_instance().TYPE_FOLDER)
        self.root = Property(self._document.get("root", {}))

    def to_dict(self):
        the_dict = super().to_dict()
        the_dict["root"] = self.root.to_dict()
        return the_dict

    def to_json_schema(self, enumerations: Enumerations, ref_stack: list = []):
        return self.root.to_json_schema(enumerations, ref_stack)

    def to_bson_schema(self, enumerations: Enumerations, ref_stack: list = []):
        return self.root.to_bson_schema(enumerations, ref_stack)
    
    @staticmethod
    def lock_all(status: bool = True):
        return ServiceBase.lock_all(Type, Config.get_instance().TYPE_FOLDER, status)

    @staticmethod
    def get_types_summary() -> list:
        """
        Return a lightweight list of type summaries for card display.
        Each item: file_name, created_at, updated_at, size, _locked, description.
        Uses FileIO.get_document for description extraction without full Property parsing.
        """
        config = Config.get_instance()
        result = []
        for file in FileIO.get_documents(config.TYPE_FOLDER):
            item = file.to_dict()
            try:
                doc = FileIO.get_document(config.TYPE_FOLDER, file.file_name)
                item["_locked"] = doc.get("_locked", False)
                item["description"] = (doc.get("root") or {}).get("description") or ""
            except Exception as e:
                logger.warning(f"Skipping {file.file_name}: {e}")
                item["_locked"] = False
                item["description"] = ""
            result.append(item)
        return result

