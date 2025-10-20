from fastapi import WebSocket, WebSocketDisconnect
from . import is_teacher, app
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}  # ip -> websocket
        self.teacher_connection: WebSocket | None = None

    async def connect(self, websocket: WebSocket, client_ip: str):
        await websocket.accept()
        self.active_connections[client_ip] = websocket
        
        # Store teacher connection separately for quick access
        if is_teacher(client_ip):
            self.teacher_connection = websocket
            print(f"Teacher connected from {client_ip}")
        else:
            print(f"Student connected from {client_ip}")

    def disconnect(self, websocket: WebSocket):
        for ip, ws in list(self.active_connections.items()):
            if ws == websocket:
                del self.active_connections[ip]
                # Clear teacher connection if teacher disconnected
                if is_teacher(ip):
                    self.teacher_connection = None
                    print(f"Teacher disconnected from {ip}")
                else:
                    print(f"Student disconnected from {ip}")
                break

    async def send_to_ip(self, message: dict, ip: str):
        if ip in self.active_connections:
            try:
                await self.active_connections[ip].send_json(message)
            except Exception as e:
                print(f"Failed to send message to {ip}: {e}")
                self.disconnect(self.active_connections[ip])

    async def send_to_teacher(self, message: dict):
        """Send message only to the teacher (127.0.0.1)"""
        if self.teacher_connection:
            try:
                await self.teacher_connection.send_json(message)
            except Exception as e:
                print(f"Failed to send message to teacher: {e}")
                self.teacher_connection = None

    async def broadcast(self, message: dict):
        for ip, connection in list(self.active_connections.items()):
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Failed to broadcast message to {ip}: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_ip = websocket.client.host
    await manager.connect(websocket, client_ip)
    try:
        while True:
            # Keep connection alive and handle ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error for {client_ip}: {e}")
        manager.disconnect(websocket)