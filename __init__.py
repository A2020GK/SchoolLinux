from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[]) 
socket_app = socketio.ASGIApp(sio)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/socket.io", socket_app)

@app.get("/test")
async def test():
    await sio.emit("info", {"status":"kill"})
    
ip_to_sid = {}
@sio.on("connect")
async def connect(sid, t):
    ip = t["asgi.scope"]["client"][0]
    ip_to_sid[ip] = sid
    print(f"New client connected: {ip} with sid = {sid}")
    
@sio.on("disconnect")
async def disconnect(sid, *args):
    try:
        ip = (list(ip_to_sid.keys())[list(ip_to_sid.values()).index(sid)])
        del ip_to_sid[ip]
        print(f"Client {ip} with sid = {sid} disconnected")
    except:
        pass

from .info import *
from .students import *