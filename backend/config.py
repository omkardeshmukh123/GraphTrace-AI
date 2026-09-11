"""
GraphTrace AI — Application Configuration
Loads settings from .env file using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="GraphTrace AI", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")

    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="", alias="NEO4J_PASSWORD")

    # File storage
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")
    extracted_dir: str = Field(default="extracted", alias="EXTRACTED_DIR")
    max_upload_size_mb: int = Field(default=100, alias="MAX_UPLOAD_SIZE_MB")

    model_config = {"env_file": (".env", "backend/.env"), "populate_by_name": True, "extra": "ignore"}

    @property
    def neo4j_username(self) -> str:
        """Alias for M3 compatibility where field is named neo4j_username."""
        return self.neo4j_user


# Singleton settings instance
settings = Settings()
