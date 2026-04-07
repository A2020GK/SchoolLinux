import logging
from .server import sio
from .manager import manager
from backend.app.config import config

logger = logging.getLogger(__name__)


def _get_header_value(scope: dict, header_name: str) -> str | None:
    headers = scope.get("headers") or []
    expected = header_name.lower().encode("latin-1")
    for key, value in headers:
        if key.lower() == expected:
            return value.decode("latin-1").strip()

    return None


def _resolve_socket_ip(environ: dict) -> str:
    scope = environ.get("asgi.scope", {})

    if config.allow_ip_override:
        debug_ip = _get_header_value(scope, config.ip_override_header)
        if debug_ip:
            return debug_ip

    client = scope.get("client")
    if client and client[0]:
        return client[0]

    return "127.0.0.1"

@sio.on("connect")
async def handle_connect(sid: str, environ: dict):
    ip = _resolve_socket_ip(environ)
    
    await manager.connect(ip, sid)
    logger.info("Client connected\t%s (sid=%s)", ip, sid)

@sio.on("disconnect")
async def handle_disconnect(sid: str):
    ip = await manager.disconnect(sid)
    if ip:
        logger.info("Client disconnected\t%s (sid=%s)", ip, sid)
    else:
        logger.warning("Unknown SID disconnected\t%s", sid)