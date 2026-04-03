import logging
from .server import sio
from .manager import manager

logger = logging.getLogger(__name__)

@sio.on("connect")
async def handle_connect(sid: str, environ: dict):
    scope = environ.get("asgi.scope", {})
    client = scope.get("client")
    ip = client[0] if client else "unknown"
    
    await manager.connect(ip, sid)
    logger.info("Client connected\t%s (sid=%s)", ip, sid)

@sio.on("disconnect")
async def handle_disconnect(sid: str):
    ip = await manager.disconnect(sid)
    if ip:
        logger.info("Client disconnected\t%s (sid=%s)", ip, sid)
    else:
        logger.warning("Unknown SID disconnected\t%s", sid)