from enum import Enum
class ProcessingEnum(str, Enum):
    txt = ".txt"
    pdf = ".pdf"
    mupdf = ".mupdf"