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
to_send_gnd_cmd = {}

ROUND_TIME_LIMIT = 15*60

ENCODING_FORMAT = "UTF-8"
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
SERVER_IP = "127.0.0.1"
# SERVER_IP = socket.gethostbyname(socket.gethostname())
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
        "direction_facing":"RIGHT",
        "health":100,
        "grenade_count":3
        
    }

def greandeCollidedWith(pid):
    pass
def clientHandler(conn,unique_id):

    global connected_clients,players,s_game_time,game_state,to_send_gnd_cmd
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
            print(cmnd)
            if cmnd.split()[0]=="move":
                players[uid]["x"]= int(cmnd.split()[1])
                players[uid]["y"]= int(cmnd.split()[2])
                players[uid]["direction_facing"] = cmnd.split()[3]
                replyToCmnd = (players,s_game_time)
            elif cmnd.split()[0]=="get":
                replyToCmnd = (players,s_game_time)

            #when a player requested to add a grenade
            elif cmnd.split()[0]=="cmd":
                if cmnd.split()[1]=="adGd":
                    rtc = "dgd "+cmnd.split()[2]+" "+cmnd.split()[3]+" "+cmnd.split()[4]+" "+str(s_game_time+1)
                    print(rtc)
                    for plr in players:
                        to_send_gnd_cmd[plr]={"msg":rtc}
                    print("464",to_send_gnd_cmd)
                    replyToCmnd = "noCommand"
                    
                elif cmnd.split()[1]=="nothing":
                    print("nothing")
                    print(to_send_gnd_cmd)
                    if uid in to_send_gnd_cmd:
                        replyToCmnd = to_send_gnd_cmd[uid]["msg"]
                        print("123" ,replyToCmnd)
                        del to_send_gnd_cmd[uid]
                    else:
                        replyToCmnd = "noCommand"
                else:
                    replyToCmnd = "noCommand"
            else:
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