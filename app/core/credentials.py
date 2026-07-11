from functools import lru_cache

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from app.core.config import settings


@lru_cache
def get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


@lru_cache
def get_project_client() -> AIProjectClient:
    if not settings.foundry_project_endpoint:
        raise RuntimeError("FOUNDRY_PROJECT_ENDPOINT is not configured")
    return AIProjectClient(
        endpoint=settings.foundry_project_endpoint,
        credential=get_credential(),
    )
