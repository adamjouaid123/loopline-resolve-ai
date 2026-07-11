from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import claims, health as health_routes
from app.core.config import settings

app = FastAPI(title="LoopLine Resolve AI")

# The React dev server (Vite) runs on a different origin during development.
# In production the UI is served as static files from the same origin, so this
# permissive CORS is a dev convenience only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_routes.router)
app.include_router(claims.router)


@app.get("/health")
def health():
    return {"status": "ok", "provider": settings.app_provider_mode}
