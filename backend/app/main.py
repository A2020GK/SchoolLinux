from .logging import *
logger = logging.getLogger(__name__)
logger.info("Starting SchoolLinux")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .socket import socket_app
from contextlib import asynccontextmanager
from .services.game import discover_and_load_games
from .state import state

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

from .routers import game
from .routers import user

app.include_router(user.router)
app.include_router(game.router)