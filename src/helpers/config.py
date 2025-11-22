from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str 
    app_version: str 
    File_ALLOWED_TYPS:list
    FILE_MAX_SIZE:int
    file_defoult_chunk_size:int
    mongo_db_url: str
    mongo_db_name: str
  
    class Config:
        env_file = ".env"


def get_settings():
    return Settings()
