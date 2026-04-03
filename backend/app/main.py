from .logging import *
logger = logging.getLogger(__name__)
logger.info("Starting SchoolLinux")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import config
from .socket import socket_app
from .state import state
from contextlib import asynccontextmanager


app = FastAPI(
    title="SchoolLinux Backend",
    version="3.0.0",
    description="Backend for SchoolLinux project. Created by A2020GK.",
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
