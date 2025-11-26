from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./notes.db"
    app_title: str = "Notes API"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()