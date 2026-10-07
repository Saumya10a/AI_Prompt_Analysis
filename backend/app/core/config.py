from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_database: str = "bda_analytics"
    
    spark_master: str = "local[2]"
    spark_app_name: str = "BDA_Analytics"
    
    dataset_path: str = "./data/sample_dataset.jsonl"
    dataset_generate_if_missing: bool = True
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
