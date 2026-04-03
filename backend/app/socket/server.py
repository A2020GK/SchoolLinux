from socketio import AsyncServer, ASGIApp

sio = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["*"],
    logger=False,
    engineio_logger=False,
)

socket_app = ASGIApp(sio)