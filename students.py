from . import app
from .data import data, Student, save
from .utils import is_teacher, send_to_ip
from pydantic import BaseModel
from fastapi import Request
from .ssh import mkclient

student_format = lambda s: {"pc":s.pc, "klads":5 - len(s.klads), "name":s.name}

def students_format():
    r = {}
    for ip, s in data.students.items():
        r[ip] = student_format(s)
    return r

update_teacher = send_to_ip("127.0.0.1", "update", students_format())

@app.get("/students")
async def students(request: Request):
    if not is_teacher(request.client.host):
        return
    return students_format()

class StudentIn(BaseModel):
    pc:str
    name:str



@app.post("/students/reg")
async def reg(student: StudentIn, request: Request):
    ip = request.client.host
    if is_teacher(ip) or ip in data.students:
        return
    
    try:
        client = mkclient(ip)
        client.close()
        data.students[ip] = Student(student.pc, student.name, set())
        save()
    
        await send_to_ip("127.0.0.1", "students", students_format())
        return student_format(data.students[ip])
    except:
        return None
    
@app.get("/students/me")
async def me(request:Request):
    if is_teacher(request.client.host) or not request.client.host in data.students:
        return None
    return student_format(data.students[request.client.host])
    
    
@app.post("/students/kick/{ip}")
async def kick(ip:str, request:Request):
    if not is_teacher(request.client.host) or ip not in data.students:
        return None
    await send_to_ip(ip, "kick")
    del data.students[ip]
    save()
    return students_format()

@app.post("/students/logout")
async def logout(request:Request):
    if is_teacher(request.client.host) or request.client.host not in data.students:
        return None
    del data.students[request.client.host]
    await send_to_ip("127.0.0.1", "students", students_format())
    return True