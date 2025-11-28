from enum import Enum

class AssetTypeEnum(str, Enum):

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    OTHER = "other"