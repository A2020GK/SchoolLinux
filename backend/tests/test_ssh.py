from __future__ import annotations

import socket
from unittest.mock import MagicMock, patch

import paramiko
import pytest

from backend.app.services.ssh import check_ip, upload_and_run_script


def test_check_ip_returns_true_on_success():
    mock_client = MagicMock()
    with patch("backend.app.services.ssh.create_client_from_config", return_value=mock_client):
        result = check_ip("192.168.1.1")

    assert result is True
    mock_client.close.assert_called_once()


def test_check_ip_returns_false_on_ssh_exception():
    with patch("backend.app.services.ssh.create_client_from_config", side_effect=paramiko.SSHException("Connection refused")):
        result = check_ip("192.168.1.2")

    assert result is False


def test_check_ip_returns_false_on_socket_error():
    with patch("backend.app.services.ssh.create_client_from_config", side_effect=socket.error("Network unreachable")):
        result = check_ip("192.168.1.3")

    assert result is False


def test_upload_and_run_script_waits_for_completion_and_returns_texts():
    client = MagicMock()
    client.get_transport.return_value.getpeername.return_value = ("10.0.0.10", 22)

    sftp = MagicMock()
    client.open_sftp.return_value = sftp
    remote_file = MagicMock()
    sftp.file.return_value.__enter__.return_value = remote_file

    stdout = MagicMock()
    stdout.channel.recv_exit_status.return_value = 0
    stdout.read.return_value = b"ok\n"
    stderr = MagicMock()
    stderr.read.return_value = b""
    client.exec_command.return_value = (MagicMock(), stdout, stderr)

    out, err = upload_and_run_script(client, "find_install", "#!/bin/bash\necho ok\n")

    sftp.file.assert_called_once_with("/tmp/find_install.sh", "w")
    remote_file.write.assert_called_once_with("#!/bin/bash\necho ok\n")
    sftp.chmod.assert_called_once_with("/tmp/find_install.sh", 0o755)
    client.exec_command.assert_called_once_with("bash /tmp/find_install.sh")
    stdout.channel.recv_exit_status.assert_called_once()
    assert out == "ok\n"
    assert err == ""


def test_upload_and_run_script_raises_when_remote_script_failed():
    client = MagicMock()
    client.get_transport.return_value.getpeername.return_value = ("10.0.0.11", 22)

    sftp = MagicMock()
    client.open_sftp.return_value = sftp
    sftp.file.return_value.__enter__.return_value = MagicMock()

    stdout = MagicMock()
    stdout.channel.recv_exit_status.return_value = 1
    stdout.read.return_value = b""
    stderr = MagicMock()
    stderr.read.return_value = b"boom"
    client.exec_command.return_value = (MagicMock(), stdout, stderr)

    with pytest.raises(RuntimeError, match="exit code 1"):
        upload_and_run_script(client, "find_install", "#!/bin/bash\nexit 1\n")
