import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from loguru import logger


def _is_docker() -> bool:
    try:
        if os.path.exists("/.dockerenv"):
            return True
        if os.path.exists("/proc/self/cgroup"):
            with open("/proc/self/cgroup") as f:
                data = f.read()
                return ("docker" in data) or ("kubepods" in data)
    except Exception:
        return False
    return False

IS_DOCKER = _is_docker()
logger.debug("IS_DOCKER: {}", IS_DOCKER)

DEFAULT_DB_DOCKER = "postgresql://postgres:postgres@db:5432/pump"
DEFAULT_DB_LOCAL = "postgresql://postgres:postgres@127.0.0.1:5432/pump"
DEFAULT_DB = DEFAULT_DB_DOCKER if IS_DOCKER else DEFAULT_DB_LOCAL
logger.info("DEFAULT_DB: {}", DEFAULT_DB)


class Settings(BaseSettings):
    database_url: str = Field(default=DEFAULT_DB)
    websocket_url: str = "wss://pumpportal.fun/api/data"
    admin_title: str = "PumpFun Admin"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

# Автоматическая коррекция DATABASE_URL при локальном запуске, если в окружении/конфиге указан host=db
if not IS_DOCKER:
    db_url = settings.database_url
    if "@db:" in db_url or "://db:" in db_url:
        fixed = db_url.replace("@db:", "@127.0.0.1:").replace("://db:", "://127.0.0.1:")
        logger.warning("DATABASE_URL points to 'db' locally. Overriding to {}", fixed)
        settings.database_url = fixed
