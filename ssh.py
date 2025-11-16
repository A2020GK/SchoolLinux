from paramiko import SSHClient, AutoAddPolicy
from os import getenv

def mkclient(ip):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(ip, username=getenv("SSH_USER"), password=getenv("SSH_PASSWORD"))
    return client