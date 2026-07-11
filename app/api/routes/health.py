"""Health and configuration endpoints for the UI."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "provider": settings.app_provider_mode}


@router.get("/config")
def config() -> dict:
    """Non-secret runtime config the UI uses for badges and feature gating."""
    return {
        "provider_mode": settings.app_provider_mode,
        "app_env": settings.app_env,
        "search_index_name": settings.search_index_name,
        "features": {
            "image_generation": settings.feature_image_generation,
            "video_generation": settings.feature_video_generation,
        },
    }
