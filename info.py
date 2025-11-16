from . import app
from fastapi import Request
from .utils import is_teacher, BaseSchema
from .data import data

class Info(BaseSchema):
    is_teacher:bool
    status:str

@app.get("/info")
async def info(request:Request) -> Info:
    return Info(is_teacher=is_teacher(request.client.host), status=data.status)
