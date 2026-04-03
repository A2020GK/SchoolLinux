import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._ip_to_sid: dict[str, str] = {}
        self._sid_to_ip: dict[str, str] = {}

    async def connect(self, ip: str, sid: str) -> None:
        self._ip_to_sid[ip] = sid
        self._sid_to_ip[sid] = ip
        logger.debug("Registered connection: %s -> %s", ip, sid)

    async def disconnect(self, sid: str) -> Optional[str]:
        ip = self._sid_to_ip.pop(sid, None)
        if ip:
            self._ip_to_sid.pop(ip, None)
            logger.debug("Cleaned up connection: %s", ip)
        return ip
    
manager = ConnectionManager()