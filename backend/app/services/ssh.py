from paramiko import SSHClient, AutoAddPolicy
from backend.app.config import config

def create_client(hostname, username, password):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    return client

def create_client_from_config(ip: str):
    return create_client(
        ip,
        config.ssh_user,
        config.ssh_password
    )

def upload_and_run_script(client: SSHClient, name: str, script: str):
    sftp = client.open_sftp()
    remote_path = f"/tmp/{name}.sh"
    with sftp.file(remote_path, "w") as remote_file:
        remote_file.write(script)
    sftp.chmod(remote_path, 0o755)
    stdin, stdout, stderr = client.exec_command(f"bash {remote_path}")
    return stdout.read(), stderr.read()
