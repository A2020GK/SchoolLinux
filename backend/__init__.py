from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .services.socket import socket_app, sio
from .models import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="SchoolLinux Backend",
    version="3.0.0",
    description="Backend for SchoolLinux project. Created by A2020GK.",
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
