from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GRAPHTRACE_", env_file=(".env", "backend/.env"), extra="ignore"
    )

    store: Literal["local", "neo4j"] = "local"
    data_dir: Path = Path(".data")
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    parser: str = ""
    graph_writer: str = ""
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: SecretStr = SecretStr("")
    neo4j_database: str = "neo4j"
    max_upload_bytes: int = Field(default=20 * 1024 * 1024, gt=0)
    max_extracted_bytes: int = Field(default=100 * 1024 * 1024, gt=0)
    max_files: int = Field(default=2000, gt=0)
    max_sidecar_bytes: int = Field(default=1024 * 1024, gt=0)
