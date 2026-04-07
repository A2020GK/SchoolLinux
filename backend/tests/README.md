# Test environment

This folder contains shared pytest scaffolding only. No actual tests are added here yet.

Available fixtures:

- `client` - FastAPI `TestClient` for synchronous HTTP testing.
- `isolated_state` - Redirects `SLData.json` to a temporary file and resets app state.
- `socketio_server` - Starts the FastAPI app under a disposable local Uvicorn server so Socket.IO can connect over HTTP/WebSocket.
- `socketio_client_factory` - Async context manager factory that opens and closes a `python-socketio` async client against the test server.

How to use the Socket.IO helper:

1. Use `socketio_server.url` as the connection target.
2. Connect with `socketio.AsyncClient` or the provided factory.
3. Prefer real server-based Socket.IO integration tests instead of trying to exercise the `/socket.io` mount with `TestClient` alone.

The setup is intentionally minimal so future tests can add markers, factories, and app-specific overrides without changing the application code.