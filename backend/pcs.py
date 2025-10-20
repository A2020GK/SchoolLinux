from fastapi import Request
from .data import data, save
from pydantic import BaseModel
from paramiko import SSHClient, AutoAddPolicy

# Import the app and functions from __init__.py
from . import app, is_teacher, manager

class RegPC(BaseModel):
    pcNumber: str
    name: str

@app.post("/pcs/reg", tags=["pcs"])
async def regpc(pc: RegPC, request: Request):
    client_ip = request.client.host
    # Only allow non-teacher IPs to register
    if not is_teacher(client_ip):
        try:
            # Check PC via SSH
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(client_ip, username="game", password="game")
            
            # Test connection with bash version
            stdin, stdout, stderr = client.exec_command("bash --version")
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
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
            else:
                print(f"SSH command failed with exit status: {exit_status}")
                return {"ok": False, "error": "SSH connection failed"}
        except Exception as e:
            print(f"Registration error: {e}")
            return {"ok": False}
        finally:
            client.close()
    return {"ok": False}

@app.get("/pcs", tags=["pcs"])
async def get_pcs(request: Request):
    if is_teacher(request.client.host):
        return data.pcs
    return {"error": "Unauthorized"}

@app.delete("/pcs/{ip}", tags=["pcs"])
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
            await manager.send_to_teacher({"type":"pc_removed", "ip":ip})
            
            return {"ok": True, "pcs": data.pcs}
    except Exception as e:
        print(f"Error deleting PC: {e}")
    return {"ok": False}