from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Котики'
    database_url: str | None = 'sqlite+aiosqlite:///./fastapi.db'
    app_description: str = 'благотворительность'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    yandex_disk_token: Optional[str] = None
    report_format: str = "%Y/%m/%d %H:%M:%S"

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
