from enum import Enum
class ResponseEnum(Enum):
    file_type_not_allowed = "File type is not allowed."
    file_size_exceeded = "File size exceeds the maximum limit."
    file_uploaded_success = "File uploaded success."
    file_uploaded_failed = "File upload failed."
    file_valid = "File is valid."
    file_processing_failed = "File processing failed."
    file_processed_success = "File processed successfully."

