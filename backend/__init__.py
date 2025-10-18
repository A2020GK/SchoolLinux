from dotenv import load_dotenv
from os import getenv
load_dotenv()

from .data import save, data
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def is_teacher(ip: str) -> bool:
    return ip == "127.0.0.1"

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

    def disconnect(self, websocket: WebSocket):
        for ip, ws in list(self.active_connections.items()):
            if ws == websocket:
                del self.active_connections[ip]
                # Clear teacher connection if teacher disconnected
                if is_teacher(ip):
                    self.teacher_connection = None
                break

    async def send_to_ip(self, message: dict, ip: str):
        if ip in self.active_connections:
            try:
                await self.active_connections[ip].send_json(message)
            except:
                self.disconnect(self.active_connections[ip])

    async def send_to_teacher(self, message: dict):
        """Send message only to the teacher (127.0.0.1)"""
        if self.teacher_connection:
            try:
                await self.teacher_connection.send_json(message)
            except:
                self.teacher_connection = None

    async def broadcast(self, message: dict):
        for ip, connection in list(self.active_connections.items()):
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@app.get("/ping")
async def ping(request: Request):
    ip = request.client.host
    isadm = is_teacher(ip)
    await manager.broadcast({"type": "ping", "message": "hai"})
    return f"pong! request ip: {ip}, isadm={isadm}"

class Status(BaseModel):
    configured: bool
    isTeacher: bool
    pcNumber: str | None
    name: str | None

@app.get("/status")
async def status(request: Request) -> Status:
    client_ip = request.client.host
    return Status(
        configured=data.configured,
        isTeacher=is_teacher(client_ip),
        pcNumber=data.pcs.get(client_ip, (None,))[0],
        name=data.pcs.get(client_ip, (None, None))[1]
    )

class RegPC(BaseModel):
    pcNumber: str
    name: str

@app.post("/regpc")
async def regpc(pc: RegPC, request: Request):
    client_ip = request.client.host
    
    # Only allow non-teacher IPs to register
    if not is_teacher(client_ip):
        try:
            r = "-".join(map(str, map(int, pc.pcNumber.strip().split("-", 1))))
            data.pcs[client_ip] = (r, pc.name)
            save()
            
            # Notify teacher about new PC registration
            await manager.send_to_teacher({
                "type": "pc_added", 
                "ip": client_ip, 
                "pcNumber": r, 
                "name": pc.name
            })
            
            return {"ok": True, "pcNumber": r}
        except Exception as e:
            print(f"Registration error: {e}")
            return {"ok": False}
    return {"ok": False}

@app.get("/pcs")
async def pcs(request: Request):
    if is_teacher(request.client.host):
        return data.pcs
    return {"error": "Unauthorized"}

@app.delete("/pcs/{ip}")
async def delpc(ip: str, request: Request):
    # Only teacher can delete PCs
    if not is_teacher(request.client.host):
        return {"ok": False, "error": "Unauthorized"}
    
    try:
        if ip in data.pcs:
            pc_data = data.pcs[ip]
            data.pcs.pop(ip)
            save()
            
            # Notify the removed PC
            await manager.send_to_ip({"type": "remove"}, ip)
            
            # Teacher doesn't need notification since they initiated the action
            # The frontend will update based on the API response
            
            return {"ok": True, "pcs": data.pcs}
    except Exception as e:
        print(f"Error deleting PC: {e}")
    return {"ok": False}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_ip = websocket.client.host
    await manager.connect(websocket, client_ip)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)