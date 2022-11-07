import socket
from _thread import *
import pickle
import time
import random 

connected_clients=0
unique_id = 0
players={}
s_game_time = "Waiting to start"
start_time=0
game_state = "NOT RUNNING"


ROUND_TIME_LIMIT = 15*60

ENCODING_FORMAT = "UTF-8"
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
SERVER_IP = "127.0.0.1"
PORT = 9999

try:
    server_socket.bind((SERVER_IP, PORT))
except Exception as e:
    print("[SERVER COULD NOT START] The following error occured:")
    print(str(e))
    quit()

server_socket.listen()

print(f"[SERVER STARTED] AT {SERVER_IP}")
print("[SERVER WAITING FOR CONNECTIONS]")

def getSpawnLocation():
    return (random.randint(10, 500),random.randint(10, 600))

def addNewPlayerToServer(data,uid):
    x,y = getSpawnLocation()
    players[uid]= {
        "name": data[1],
        "adm": data[0],
        "score": 0,
        "characterType":0,
        "x":x,
        "y":y,
        "direction_facing":"RIGHT"
        
    }


def clientHandler(conn,unique_id):

    global connected_clients,players,s_game_time,game_state
    uid=unique_id
    data = pickle.loads(conn.recv(2048))
    name = data[1]
    print("[LOG]",name,"Connected to the server")
    addNewPlayerToServer(data,uid)
    conn.send(str(uid).encode(ENCODING_FORMAT))

    while True:
        if game_state == "RUNNING":
            s_game_time  = round(time.time()-start_time)
            if s_game_time >= ROUND_TIME_LIMIT:
                game_state = "RUNNING"
        try:
            cmnd = conn.recv(64)
            if not cmnd:
                break

            cmnd = cmnd.decode(ENCODING_FORMAT)
            #apply cmnd to player in ther server
            #replyToCmnd = (players,s_game_time)
            if cmnd.split()[0]=="move":
                players[uid]["x"]= int(cmnd.split()[1])
                players[uid]["y"]= int(cmnd.split()[2])
                players[uid]["direction_facing"] = cmnd.split()[3]
            # print(players[uid])
            replyToCmnd = (players,s_game_time)
            # print(replyToCmnd)
            conn.send(pickle.dumps(replyToCmnd))
        except Exception as e:
            print(e)
            break


        
    print("[DISCONNECTED]",name,"disconnected from the server")
    connected_clients-=1
    del players[uid]
    conn.close()



while True:
    conn,addr = server_socket.accept()
    connected_clients+=1
    if connected_clients == 1 and game_state == "NOT RUNNING":
        game_state = "RUNNING"
        start_time=time.time()
        print("[LOG] Game Started")

    print("[NEW CONNECTION] Connected to: ",addr)
    start_new_thread(clientHandler,(conn,unique_id))
    unique_id+=1