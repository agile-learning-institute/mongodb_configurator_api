import os
import json
import yaml
from datetime import datetime
from pathlib import Path

from configurator.utils.config import Config
from configurator.utils.configurator_exception import ConfiguratorEvent, ConfiguratorException

import logging
logger = logging.getLogger(__name__)

class File:
    """Class representing a file with its properties."""
    
    def __init__(self, file_path: str):
        """Initialize a File instance with file properties."""
        self.file_name = os.path.basename(file_path)
        self.created_at = None
        self.updated_at = None
        self.size = 0
        
        # Get file properties if file exists
        try:
            stat = os.stat(file_path)
            self.size = stat.st_size
            self.created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
            self.updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except Exception as e:
            event = ConfiguratorEvent(event_id="FIL-01", event_type="GET_FILE_PROPERTIES", event_data={"error": str(e)})
            raise ConfiguratorException(f"Failed to get file properties for {file_path}", event)

    def to_dict(self):
        """Convert file properties to dictionary matching OpenAPI schema (flat)."""
        return {
            "file_name": self.file_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "size": self.size
        }


class FileIO:
    """Class for file I/O operations."""
    
    @staticmethod
    def get_documents(folder_name: str) -> list[File]:
        """Get all files from a folder."""
        config = Config.get_instance()
        folder = os.path.join(config.INPUT_FOLDER, folder_name)
        files = []
        
        try:
            if not os.path.exists(folder):
                event = ConfiguratorEvent(event_id="FIL-03", event_type="GET_DOCUMENTS")
                event.record_failure("Folder not found")
                raise ConfiguratorException(f"Folder not found: {folder}", event)
            
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                if os.path.isfile(file_path):
                    files.append(File(file_path))
            return files
        except ConfiguratorException:
            raise
        except Exception as e:
            event = ConfiguratorEvent(event_id="FIL-03", event_type="GET_DOCUMENTS")
            event.record_failure(str(e))
            raise ConfiguratorException(f"Failed to get documents from {folder}", event)
    
    @staticmethod
    def get_document(folder_name: str, file_name: str) -> dict:
        """Read document content from a file."""
        config = Config.get_instance()
        folder = os.path.join(config.INPUT_FOLDER, folder_name)
        file_path = os.path.join(folder, file_name)
        extension = os.path.splitext(file_path)[1].lower()
        
        # Check for unsupported file types
        if extension not in [".yaml", ".json"]:
            event = ConfiguratorEvent(event_id="FIL-06", event_type="UNSUPPORTED_FILE_TYPE")
            event.record_failure(f"Unsupported file type: {extension}")
            raise ConfiguratorException(f"Unsupported file type: {extension}", event)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if extension == ".yaml":
                    return yaml.safe_load(f)
                elif extension == ".json":
                    return json.loads(f.read())
        except FileNotFoundError:
            event = ConfiguratorEvent(event_id="FIL-06", event_type="GET_DOCUMENT")
            event.record_failure("File not found")
            raise ConfiguratorException(f"File not found: {file_path}", event)
        except Exception as e:
            event = ConfiguratorEvent(event_id="FIL-06", event_type="GET_DOCUMENT")
            event.record_failure(str(e))
            raise ConfiguratorException(f"Failed to get document from {file_path}", event)
    
    @staticmethod
    def put_document(folder_name: str, file_name: str, document: dict) -> dict:
        """Write document content to a file."""
        config = Config.get_instance()
        folder = os.path.join(config.INPUT_FOLDER, folder_name)
        file_path = os.path.join(folder, file_name)
        extension = os.path.splitext(file_path)[1].lower()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if extension == ".yaml":
                    yaml.dump(document, f)
                elif extension == ".json":
                    f.write(json.dumps(document, indent=2))
            
        except Exception as e:
            event = ConfiguratorEvent(event_id="FIL-08", event_type="PUT_DOCUMENT")
            event.record_failure(str(e))
            raise ConfiguratorException(f"Failed to put document to {file_path}", event)
        return FileIO.get_document(folder_name, file_name)
    
    @staticmethod
    def delete_document(folder_name: str, file_name: str) -> ConfiguratorEvent:
        config = Config.get_instance()
        folder = os.path.join(config.INPUT_FOLDER, folder_name)
        file_path = os.path.join(folder, file_name)
        
        event = ConfiguratorEvent(event_id="FIL-09", event_type="DELETE_DOCUMENT")
        
        try:
            os.remove(file_path)
            event.record_success()
            return event
        except FileNotFoundError:
            event.record_failure("File not found")
            raise ConfiguratorException(f"Failed to delete {file_name} from {folder_name}", event)
        except Exception as e:
            event.record_failure(str(e))
            raise ConfiguratorException(f"Failed to delete {file_name} from {folder_name}", event)
    
    @staticmethod
    def file_exists(folder_name: str, file_name: str) -> bool:
        """Check if a file exists in the specified folder."""
        config = Config.get_instance()
        folder = os.path.join(config.INPUT_FOLDER, folder_name)
        file_path = os.path.join(folder, file_name)
        
        try:
            return os.path.isfile(file_path)
        except Exception as e:
            event = ConfiguratorEvent(event_id="FIL-10", event_type="FILE_EXISTS")
            event.record_failure(str(e))
            raise ConfiguratorException(f"Failed to check if file exists: {file_path}", event)
    