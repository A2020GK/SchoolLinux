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
    ip = client.get_transport().getpeername()[0]
    logger.info(f"Uploading script {name} to ip {ip}")
    sftp = client.open_sftp()
    remote_path = f"/tmp/{name}.sh"
    with sftp.file(remote_path, "w") as remote_file:
        remote_file.write(script)
    sftp.chmod(remote_path, 0o755)
    _, stdout, stderr = client.exec_command(f"bash {remote_path}")

    # Wait for completion before returning. Otherwise caller may close SSH client
    # and terminate script in the middle, producing partial game files.
    exit_code = stdout.channel.recv_exit_status()
    stdout_text = stdout.read().decode("utf-8", errors="replace")
    stderr_text = stderr.read().decode("utf-8", errors="replace")

    if exit_code != 0:
        logger.error(
            "Script %s failed on ip %s with exit code %s. stderr: %s",
            name,
            ip,
            exit_code,
            stderr_text.strip(),
        )
        raise RuntimeError(
            f"Script {name} failed on {ip} with exit code {exit_code}: {stderr_text.strip() or stdout_text.strip()}"
        )

    logger.info(f"Script {name} executed on ip {ip}")
    return stdout_text, stderr_text
