from . import app, sio, ip_to_sid
from fastapi import Request
from .utils import is_teacher, BaseSchema, send_to_ip
from .data import data, save
from .generator import mktree
from .students import student_format, students_format


def mkcsv():
    lines = ["IP;Компьютер;Имя;Клады"]
    for ip, d in data.students.items():
        lines.append(";".join((ip, d.pc, d.name, str(5 - len(d.klads)))))
    return "\n".join(lines)

@app.post("/game/start")
async def start(request: Request):
    if not is_teacher(request.client.host):
        return
    
    data.status = "init"
    await sio.emit("info", {"status":data.status})
    
    for ip in filter(lambda t: not is_teacher(t) and t in data.students, ip_to_sid):
        data.students[ip].klads = set(mktree(ip))
                
    data.status = "run"
    save()
    
    for ip in filter(lambda t: not is_teacher(t) and t in data.students, ip_to_sid):
        await send_to_ip(ip, "update", student_format(data.students[ip]))
    
    await sio.emit("info", {"status":data.status})
    return students_format()

@app.post("/game/stop")
async def stop(request:Request):
    if not is_teacher(request.client.host) or data.status not in ("init", "run"):
        return
    
    data.status = "reg"
    await sio.emit("info", {"status":data.status})
    return mkcsv()
    
class Klad(BaseSchema):
    value:str

@app.post("/game/klad")
async def klad(klade:Klad, request:Request):
    klad = klade.value
    if is_teacher(request.client.host) or data.status != "run" or not request.client.host in data.students or klad  not in data.students[request.client.host].klads:
        return
    data.students[request.client.host].klads.discard(klad)
    save()
    await send_to_ip("127.0.0.1", "students", students_format())
    return student_format(data.students[request.client.host])
    