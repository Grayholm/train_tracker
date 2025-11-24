from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class EmailSettings(BaseSettings):
    email_host: str
    email_port: int
    email_username: str
    email_password: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

class RedisSettings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

class Settings(BaseSettings):
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    email_settings: EmailSettings = EmailSettings()
    redis_settings: RedisSettings = RedisSettings()
    secret_key: SecretStr
    templates_dir: str = "templates"
    frontend_url: str

    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
