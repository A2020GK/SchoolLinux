from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from . import sio, ip_to_sid

is_teacher = lambda r: r == "127.0.0.1"
# is_teacher = lambda r: False

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

async def send_to_ip(ip, event, data=None):
    if ip in ip_to_sid:
        await sio.emit(event, data, ip_to_sid[ip])