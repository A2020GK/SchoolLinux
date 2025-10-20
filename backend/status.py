from . import app, is_teacher
from .data import data
from pydantic import BaseModel
from fastapi import Request

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