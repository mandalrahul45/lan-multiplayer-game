import socket
import pickle

class Connection:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.port = 9999
        self.host = "127.0.0.1"

    # TO DO: Create another parameterized constructor 


    def connect(self, adm,name):
        print("in c 1")
        self.client_socket.connect((self.host,self.port))
        print("in c 2")

        self.client_socket.send(pickle.dumps((adm,name)))
        print("in c 3")

        #raw_data receives a unique id from the server
        raw_data = self.client_socket.recv(8)
        print("in c 4")

        return int(raw_data.decode("utf-8"))

    def send(self,data,serialize=False):

        try:
            if serialize:
                self.client_socket.send(pickle.dumps(data))
            else:
                self.client_socket.send(str(data).encode("utf-8"))
                
            reply = self.client_socket.recv(2048*4)
            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print("[NO REPLY FROM SERVER] The following error occured:")
                print(e)
            return reply
        except Exception as e:
            print("[FAILED TO CONNECT] The following error occured:")
            print(e)
    
    def disconnect(self):
        self.client_socket.close()