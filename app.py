from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
from data import data, save
from ssh import mkclient
from generator import mktree

app = Flask(__name__)
socketio = SocketIO(app)

is_teacher = lambda: request.remote_addr == "127.0.0.1"

def user():
    r = data.users.get(request.remote_addr, {})
    r["is_teacher"] = is_teacher()
    # r["is_teacher"] = False
    return r
    

@app.route("/")
def homepage():
    u = user()
    if "klads" in u and u["klads"] != None:
        k = len(u["klads"]) == 0
    else:
        k = False
    return render_template("index.html", user=user(), status=data.status, kladsNo = k)

@app.route("/config")
def config():
    if not is_teacher():
        return redirect("/")
    print(data.users)
    return render_template("config.html", users=data.users)

@app.route("/logout")
def logout():
    if request.remote_addr in data.users:
        del data.users[request.remote_addr]
        update_tlist()
        save()
    return redirect("/")

@socketio.on("newpc")
def new(msg):
    try:
        client = mkclient(request.remote_addr)
        client.close()
        print("NewPC")
        data.users[request.remote_addr] = msg
        data.users[request.remote_addr]["klads"] = None
        update_tlist()
        save()
        return "ok"
    except Exception as e:
        print(e)
        return "error"
    finally:
        client.close()
        
ip_to_socket = {}
update_tlist = lambda: send_to_ip("127.0.0.1", "pcchange", [{"ip":i, "name":m["name"], "pc":m["pc"]} for i, m in data.users.items()])

def send_to_ip(target_ip, event_name, data = {}):
    """Send message to client with specific IP address"""
    if target_ip in ip_to_socket:
        socket_id = ip_to_socket[target_ip]
        socketio.emit(event_name, data, room=socket_id)
        print(f"Sent to {target_ip}: {data}")
        return True
    else:
        print(f"Client with IP {target_ip} not found")
        return False
    
@socketio.on("connect")
def connect():
    ip_to_socket[request.remote_addr] = request.sid

@socketio.on('disconnect')
def handle_disconnect():
    if request.remote_addr in ip_to_socket:
        del ip_to_socket[request.remote_addr]
        update_tlist()
        
@socketio.on("tup")
def tup():
    update_tlist()
    
@socketio.on("kick")
def kick(r):
    ip = r["ip"]
    if ip in data.users:
        print(f"Kicking user {ip}")
        del data.users[ip]
        send_to_ip(ip, "kick")
        update_tlist()
        return "ok";
    return "error";

@socketio.on("begin")
def begin():
    emit("begin", broadcast=True)
    data.status = "starting"
    if len(data.users) == 0:
        return
    for ip in filter(lambda t: t != "127.0.0.1", ip_to_socket.keys()):
        data.users[ip]["klads"] = set(mktree(ip))
        save()
    data.status = "run"
    save()
    emit("run", broadcast=True)
    update_tlist()

@socketio.on("klad")
def klad(m):
    k = m["klad"]
    if k in data.users[request.remote_addr]["klads"]:
        data.users[request.remote_addr]["klads"].discard(k)
        save()
        update_tlist()
        return {"status":"ok", "left":len(data.users[request.remote_addr]["klads"])}
    return {"status":"error", "left":len(data.users[request.remote_addr]["klads"])}