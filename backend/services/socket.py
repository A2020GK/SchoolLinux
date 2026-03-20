from socketio import AsyncServer, ASGIApp
from fastapi import FastAPI

sio = AsyncServer(async_mode="asgi", cors_allowed_origins=[]) 
socket_app = ASGIApp(sio)

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

