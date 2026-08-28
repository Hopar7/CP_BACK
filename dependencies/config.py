import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class DefaultConfig(BaseSettings):
    postgresql_endpoint: str = os.getenv("POSTGRESQL_ENDPOINT", "svc.sel4.cloudtype.app")
    postgresql_port: int = os.getenv("POSTGRESQL_PORT", "32700")
    postgresql_table: str = os.getenv("POSTGRESQL_TABLE", "reaction_db")
    postgresql_user: str = os.getenv("POSTGRESQL_USER", "root")
    postgresql_password: str = os.getenv("POSTGRESQL_PASSWORD", "3321")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "5c2fea6305c8c209714e73b265958703e65c4b40dec4c388dddac06f3f791ec7",
    )
    jwt_expire_minutes: int = os.getenv("JWT_TOKEN_EXPIRE_MINUTES", 600)


@lru_cache
def get_config():
    return DefaultConfig()
