from backend.app.state import state
from ipaddress import ip_address
from backend.app.schemas.user import User, RegisterRequest

def get_user_by_ip(ip: str):
    return state.data.users.get(ip)

def is_teacher(ip: str):
    return ip_address(ip).is_loopback

def register_user(request: RegisterRequest, ip: str):
    if is_teacher(ip):
        return None, False
    
    user = get_user_by_ip(ip)
    if user is not None:
        return user, False
    
    new_user = User(
        ip=ip,
        score=0,
        kicked=False,
        game_data={}
    )
    state.data.users[ip] = new_user
    state.save()
    return new_user, True

def get_all_users():
    return list(state.data.users.values())

def set_kicked(ip: str, kicked: bool):
    user = get_user_by_ip(ip)
    if user is not None:
        user.kicked = kicked
        state.save()
        return True
    return False
