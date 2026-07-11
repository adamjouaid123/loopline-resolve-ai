from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_provider_mode: Literal["azure", "local", "mock"] = "mock"
    log_level: str = "INFO"

    foundry_project_endpoint: str | None = None
    foundry_chat_model: str | None = None
    foundry_multimodal_model: str | None = None
    foundry_embedding_model: str | None = None

    search_endpoint: str | None = None
    search_index_name: str = "loopline-knowledge"

    feature_image_generation: bool = False
    feature_video_generation: bool = False
    agent_max_steps: int = 6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
