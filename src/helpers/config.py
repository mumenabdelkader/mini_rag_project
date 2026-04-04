from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str 
    app_version: str 
    File_ALLOWED_TYPS:list
    FILE_MAX_SIZE:int
    file_defoult_chunk_size:int
    mongo_db_url: str
    mongo_db_name: str
    
    GENERATION_BACKEND:str
    EMPEDING_BACKEND:str
    OPENAI_API_KEY:str
    OPENAI_API_URL:str
    COHERE_API_KEY:str

    GENERATION_MODEL_ID:str
    EMPEDDING_MODEL_ID:str
    EMPEDDING_MODEL_SIZE:int

    INPUT_DEFOULT_MAX_SIZE:int
    GENERATION_DEFOULT_TOKENS:int
    GENERATION_DEFOULT_TEMPRETUR:float

    VECTOR_DB_BACKEND:str
    VECTOR_DB_PATH:str
    VECTOR_DB_DISTANCE_METHOD:str

    DEFOULT_LANGUAGE:str
    PRIMARY_LANGUAGE:str

  
    class Config:
        env_file = ".env"


def get_settings():
    return Settings()
