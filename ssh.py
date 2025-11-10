from paramiko import SSHClient, AutoAddPolicy
def mkclient(ip):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(ip, username="game", password="game")
    return client