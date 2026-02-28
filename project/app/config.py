from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file='.env', extra='ignore', case_sensitive=False)

    DATABASE_URL: str = 'postgresql://postgres:postgres@localhost:5432/appdb'
    SECRET_KEY: str = 'supersecretkey-change-in-production'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()

