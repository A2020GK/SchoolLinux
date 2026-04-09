from __future__ import annotations

import socket
from unittest.mock import MagicMock, patch

import paramiko

from backend.app.services.ssh import check_ip


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
