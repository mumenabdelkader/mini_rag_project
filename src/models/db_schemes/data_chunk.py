from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    chunk_txt: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: str
    chunk_asset_id: str

    # -------- Validators -------- #
    @field_validator("chunk_project_id", "id", mode="before")
    def validate_objectid(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        try:
            return str(ObjectId(v))
        except:
            raise ValueError("Invalid ObjectId format")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False
            },
            
        ]
