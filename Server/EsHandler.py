from elasticsearch import Elasticsearch
from prettytable import PrettyTable
import json




class EsHandler:

    def __init__(self, db_name, es_url):
        self.pt = PrettyTable()
        self.db_name = db_name
        self.es = Elasticsearch(es_url)



    #tabulate es date using prettytable
    def tabulate_data(self, resp):
        for hit in resp['hits']['hits']:
            self.pt.field_names = ["Client ID", "Mac Address", "IP Address", "System", "Node Name", "Release", "Version", "Machine", "Date-Joined", "Time-Joined", "User"]
            self.pt.add_row([
                         hit["_id"],
                         hit["_source"].get("mac-address"),
                         hit["_source"].get("ip"),
                         hit["_source"].get("os"),
                         hit["_source"].get("node-name"),
                         hit["_source"].get("release"),
                         hit["_source"].get("version"),
                         hit["_source"].get("machine"),
                         hit["_source"].get("date-joined"),
                         hit["_source"].get("time-joined"),
                         hit["_source"].get("user")
                         ])

        print(self.pt)
        self.pt.clear()



    #saves first portion of client file in index
    def store_client_information(self, client_info):
            client_info = eval(client_info.replace("'", "\"")) # Convert the string to a Python dictionary
            doc = json.dumps(client_info, indent=4, ensure_ascii=False)

            try:
                #store client info in elasticsearch index 
                resp = self.es.index(index=self.db_name, document=doc)
            except Exception as e:
                print("[+]Unable to store data!!!")
                print(e)


    #retrieve client information documents from elastic search
    def retrieve_client_information(self):
        try:
            response = self.es.search(index=self.db_name, size=100, query={"match_all": {}})
            self.tabulate_data(response)
        except Exception as e:
                print(e)


    #deletes client document from index
    def delete_doc(self, client_id):
        try:
            self.es.delete(index=self.db_name, id=client_id)
            print("[+]Document deleted sucessfully!!! \n")
        except:
            print("[-]Document does not exist!!! \n")



    #deletes all documents in specified index
    def delete_all_docs(self):
        try:
            self.es.delete_by_query(index=self.db_name, body={"query": {"match_all": {}}})
            print("[+]Documents deleted sucessfully!!!")
        except Exception as e:
            print(e)
            print("[+]Unable delete documents")


    #retrieves the specified feilds in a document
    def show_fields(self, client_id):
        try:
            resp = self.es.get(index=self.db_name, id=client_id)
            self.pt.field_names = ["Client Fields"]

            for field in resp["_source"].keys():
                self.pt.add_row([field])
           
            print(self.pt)
            self.pt.clear()

        except Exception as e:
            print("[-]Document does not exist!!! /n")




    #retrieves the specified feilds in a document
    def get_field(self, client_id, feild_parameter):
        try:
            resp = self.es.get(index=self.db_name, id=client_id)
            resp = resp['_source'].get(feild_parameter)

            if resp == "null":
                print("[-]Field does not exist")
            else:
                print(json.dumps(resp, indent=4))
        except:
            print("[-]Field does not exist")


