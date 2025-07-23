from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/censo_escolar"
    debug: bool = True

settings = Settings()