from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MYSQL_USER: str | None = None
    MYSQL_PASSWORD: str | None = None
    MYSQL_HOST: str | None = None
    MYSQL_PORT: int = 3306
    MYSQL_SCHEMA: str | None = None

    NAVER_SEARCH_CLIENT_ID: str
    NAVER_SEARCH_CLIENT_SECRET: str
    NAVER_DATALAB_CLIENT_ID: str
    NAVER_DATALAB_CLIENT_SECRET: str

    NAVER_MAP_CLIENT_ID: str | None = None
    NAVER_MAP_CLIENT_SECRET: str | None = None

    CORS_ORIGINS: list[str] = []

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SERVICE_NAME: str = "MJE"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
