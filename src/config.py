import os

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env='postgres_url')
    redis_url: str = Field(default='redis://localhost:6379/0', env='redis_url')
    service2_url: str = Field(default='http://localhost:8001', env='service2_url')
    cb_fail_max: int = 5
    cb_reset_timeout: int = 30
    retry_max_attempts: int = 3
    retry_min_wait: float = 1.0
    retry_max_wait: float = 8.0

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')