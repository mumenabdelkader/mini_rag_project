from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)

    @field_validator("id", mode="before")                 #هو مش حاططها 
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        return value

    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True   # يسمح باستخدام الاسم الأصلي أو alias
    }

    @classmethod
    def get_indexes(cls):
        return [
           { 
               "key":[("project_id", 1)],
               "name":"project_id_index_1",
                "unique":True
            
            }
            ]
