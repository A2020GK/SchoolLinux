import logging
from typing import Optional
from ipaddress import ip_address

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._ip_to_sid: dict[str, str] = {}
        self._sid_to_ip: dict[str, str] = {}
        self._teacher_ip: str = "127.0.0.1"

    async def connect(self, ip: str, sid: str) -> None:
        self._ip_to_sid[ip] = sid
        self._sid_to_ip[sid] = ip
        try:
            if ip_address(ip).is_loopback:
                logger.info("Teacher connected: %s (sid=%s)", ip, sid)
                self._teacher_ip = ip
        except ValueError:
            logger.warning("Received invalid IP on connect: %s (sid=%s)", ip, sid)
        logger.debug("Registered connection: %s -> %s", ip, sid)

    async def disconnect(self, sid: str) -> Optional[str]:
        ip = self._sid_to_ip.pop(sid, None)
        if ip:
            self._ip_to_sid.pop(ip, None)
            logger.debug("Cleaned up connection: %s", ip)
        return ip
    
    async def send_to_ip(self, ip: str, event: str, data) -> bool:
        sid = self._ip_to_sid.get(ip)
        if sid:
            from .server import sio  # Import here to avoid circular import
            await sio.emit(event, data, to=sid)
            logger.debug("Sent event '%s' to %s (sid=%s)", event, ip, sid)
            return True
        logger.warning("No active connection for IP %s", ip)
        return False
    
    async def send_to_teacher(self, event: str, data) -> bool:
        return await self.send_to_ip(self._teacher_ip, event, data)

    async def send_to_everyone(self, event: str, data) -> None:
        for ip in list(self._ip_to_sid.keys()):
            await self.send_to_ip(ip, event, data)
    
    async def send_to_everyone_except_teacher(self, event: str, data) -> None:
        for ip in list(self._ip_to_sid.keys()):
            if ip != self._teacher_ip:
                await self.send_to_ip(ip, event, data)
    
manager = ConnectionManager()