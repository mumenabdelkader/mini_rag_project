from enum import Enum

class DataBaseEnum(str, Enum):
    collection_project_name = "projects"
    collection_chunk_name = "chunks"