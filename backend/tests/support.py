from __future__ import annotations

import socket
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass

import socketio
import uvicorn
from fastapi import FastAPI


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_server(server: uvicorn.Server, timeout: float = 10.0) -> None:
    started_at = time.monotonic()
    while not getattr(server, "started", False):
        if time.monotonic() - started_at > timeout:
            raise RuntimeError("Timed out waiting for the Socket.IO test server to start.")
        time.sleep(0.05)


@dataclass(slots=True)
class SocketIOServerHandle:
    url: str
    server: uvicorn.Server
    thread: threading.Thread

    def close(self) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)


def start_test_server(app: FastAPI) -> SocketIOServerHandle:
    port = find_free_port()
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        lifespan="on",
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    wait_for_server(server)
    return SocketIOServerHandle(url=f"http://127.0.0.1:{port}", server=server, thread=thread)


@asynccontextmanager
async def create_socketio_client(url: str, **connect_kwargs):
    client = socketio.AsyncClient()
    connect_kwargs.setdefault("transports", ["websocket"])
    await client.connect(url, **connect_kwargs)
    try:
        yield client
    finally:
        await client.disconnect()