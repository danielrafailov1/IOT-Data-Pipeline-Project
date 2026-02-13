from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "zebrastream"
    postgres_user: str = "zebra_app"
    postgres_password: str = ""
    openai_api_key: str = ""
    testing: bool = False

    @property
    def database_url(self) -> str:
        if self.testing:
            return "sqlite:///:memory:"
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
