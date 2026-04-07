from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.config import config
from backend.app.main import app as fastapi_app
from backend.app.state import AppData, state

from backend.tests.support import create_socketio_client, start_test_server


@pytest.fixture()
def isolated_state(tmp_path: Path):
    original_path = state._path
    original_data = state.data.model_copy(deep=True)
    original_allow_ip_override = config.allow_ip_override

    state._path = tmp_path / "SLData.test.json"
    state.data = AppData()
    state.save()
    config.allow_ip_override = True

    try:
        yield state
    finally:
        state._path = original_path
        state.data = original_data
        config.allow_ip_override = original_allow_ip_override


@pytest.fixture()
def client(isolated_state):
    with TestClient(fastapi_app) as test_client:
        yield test_client


@pytest.fixture()
def socketio_server(isolated_state):
    handle = start_test_server(fastapi_app)
    try:
        yield handle
    finally:
        handle.close()


@pytest.fixture()
def socketio_client_factory(socketio_server):
    @asynccontextmanager
    async def factory(**connect_kwargs):
        async with create_socketio_client(socketio_server.url, **connect_kwargs) as client:
            yield client

    return factory