from pathlib import Path

from .logging import *
logger = logging.getLogger(__name__)
logger.info("Starting SchoolLinux")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .socket import socket_app
from contextlib import asynccontextmanager
from .services.game import discover_and_load_games
from .state import state
from .routers import game
from .routers import user

_FRONTEND_DIST_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"
_FRONTEND_INDEX_FILE = _FRONTEND_DIST_DIR / "index.html"
_NON_FRONTEND_SEGMENTS = {"game", "user", "socket.io", "ping", "docs", "redoc", "openapi.json"}


def _resolve_frontend_asset(full_path: str) -> Path | None:
    if not full_path:
        return None

    asset_path = (_FRONTEND_DIST_DIR / full_path).resolve()
    try:
        asset_path.relative_to(_FRONTEND_DIST_DIR)
    except ValueError:
        return None

    if asset_path.is_file():
        return asset_path
    return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    state.reload()
    discover_and_load_games()
    yield
    

app = FastAPI(
    title="SchoolLinux Backend",
    version="3.0.0",
    description="Backend for SchoolLinux project. Developed by Antony.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/socket.io", socket_app)

@app.get("/ping", tags=["Healthcheck"])
async def ping():
    """Endpoint for checking if the server is alive. Returns "pong" if the server is running."""
    return "pong"

app.include_router(user.router)
app.include_router(game.router)


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    if not _FRONTEND_INDEX_FILE.is_file():
        raise HTTPException(status_code=404, detail="Not Found")

    first_segment = full_path.split("/", 1)[0] if full_path else ""
    if first_segment in _NON_FRONTEND_SEGMENTS:
        raise HTTPException(status_code=404, detail="Not Found")

    asset = _resolve_frontend_asset(full_path)
    if asset is not None:
        return FileResponse(asset)

    return FileResponse(_FRONTEND_INDEX_FILE)