import socket

from paramiko import SSHException, SSHClient, AutoAddPolicy
from backend.app.config import config
import logging

logger = logging.getLogger(__name__)

def create_client(hostname, username, password, timeout: float):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(
        hostname,
        username=username,
        password=password,
        timeout=timeout,
        auth_timeout=timeout,
        banner_timeout=timeout,
    )
    return client

def create_client_from_config(ip: str):
    return create_client(
        ip,
        config.ssh_user,
        config.ssh_password,
        config.ssh_timeout,
    )
    
def execute_command(client: SSHClient, command: str):
    logger.info(f"Executing command '{command}' on ip {client.get_transport().getpeername()[0]}")
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.read().decode("utf-8"), stderr.read().decode("utf-8")

def check_ip(ip: str) -> bool:
    try:
        client = create_client_from_config(ip)
        client.close()
        return True
    except Exception:
        return False

def upload_and_run_script(client: SSHClient, name: str, script: str):
    logger.info(f"Uploading script {name} to ip {client.get_transport().getpeername()[0]}")
    sftp = client.open_sftp()
    remote_path = f"/tmp/{name}.sh"
    with sftp.file(remote_path, "w") as remote_file:
        remote_file.write(script)
    sftp.chmod(remote_path, 0o755)
    stdin, stdout, stderr= client.exec_command(f"bash {remote_path}")
    logger.info(f"Script {name} executed on ip {client.get_transport().getpeername()[0]}")
    return stdout, stderr
