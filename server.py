import socket
from _thread import *
import pickle
import time
import random 
import json
connected_clients=0
unique_id = 0
players={}
s_game_time = "0"
start_time=0
game_state = "NOT RUNNING"
to_send_gnd_cmd = {}

ROUND_TIME_LIMIT = 15*60

ENCODING_FORMAT = "UTF-8"
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# SERVER_IP = "127.0.0.1"
SERVER_IP = socket.gethostbyname(socket.gethostname())
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
    spawnLocations=[[14,17],
                    [25,9],
                    [23,17],
                    [13,11],
                    # [51,16],
                    # [43,11],
                    [30,13]]
    spawnLoc = random.choice(spawnLocations)
    return (spawnLoc[0]*128,spawnLoc[1]*128)

def addNewPlayerToServer(data,uid,addr):
    x,y = getSpawnLocation()
    players[uid]= {
        "name": data[1],
        "adm": data[0],
        "score": 0,
        "characterType":0,
        "x":x,
        "y":y,
        "direction_facing":"RIGHT",
        "health":500,
        "grenade_count":3,
        "ip":addr
    }


def save_playerInfo():
    while True:
        if int(s_game_time) %10==0:
            try:
                with open('players_list.txt') as plr_listFile:
                    saved_data = json.load(plr_listFile)
            except:
                saved_data={}
            for plr in players:
                saved_data[plr] = players[plr]
            with open('players_list.txt',"w") as plr_listFile:
                json.dump(saved_data,plr_listFile)

def threaded_grenade_handler():
    upd_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    upd_server.bind((socket.gethostbyname(socket.gethostname()),9696))
    while True:
        start_new_thread(threaded_grenade_handler2,(upd_server,))
        
def threaded_grenade_handler2(upd_server):
    cmnd,addrs = upd_server.recvfrom(1024*3)   
    if cmnd.split()[0]=="adGd":
        rtc = "dgd "+cmnd.split()[2-1]+" "+cmnd.split()[3-1]+" "+cmnd.split()[4-1]
        print(rtc)
        for plr in players:
            upd_server.sendto(rtc,(players[plr]["ip"],9696))
    
            
    

    
def clientHandler(conn,unique_id,addr):

    global connected_clients,players,s_game_time,game_state,to_send_gnd_cmd
    uid=unique_id
    data = pickle.loads(conn.recv(2048))
    name = data[1]
    print("[LOG]",name,"Connected to the server")
    addNewPlayerToServer(data,uid,addr)
    conn.send(str(uid).encode(ENCODING_FORMAT))

    while True:
        replyToCmnd2 = "noCommand"

        if game_state == "RUNNING":
            s_game_time  = round(time.time()-start_time)
            if s_game_time >= ROUND_TIME_LIMIT:
                game_state = "RUNNING"
        try:
            cmnd = conn.recv(2048*5)
            if not cmnd:
                break

            cmnd = pickle.loads(cmnd)#cmnd.decode(ENCODING_FORMAT)
            #apply cmnd to player in ther server
            #replyToCmnd = (players,s_game_time)
            print(cmnd)
            if cmnd[0].split()[0]=="move":
                players[uid]["x"]= int(cmnd[0].split()[1])
                players[uid]["y"]= int(cmnd[0].split()[2])
                players[uid]["direction_facing"] = cmnd[0].split()[3]
                replyToCmnd = (players,s_game_time,replyToCmnd2)
            elif cmnd[0].split()[0]=="get":
                replyToCmnd = (players,s_game_time,replyToCmnd2)
            elif cmnd[0].split()[0]=="closeConn":
                print("[DISCONNECTED]",name,"disconnected from the server")
                connected_clients-=1
                del players[uid]
                conn.close()
                break
            else:
                replyToCmnd = (players,s_game_time,replyToCmnd2)

            # when a player requested to add a grenade
            if cmnd[1].split()[0]=="adGd":
                rtc = "dgd "+cmnd[1].split()[1]+" "+cmnd[1].split()[2]+" "+cmnd[1].split()[3]+" "+cmnd[1].split()[4]
                print(rtc)
                for plr in players:
                    to_send_gnd_cmd[plr]={"msg":rtc}
                print("464",to_send_gnd_cmd)
                    
                    
            
                
            if uid in to_send_gnd_cmd:
                replyToCmnd2 = to_send_gnd_cmd[uid]["msg"]
                replyToCmnd = (players,s_game_time,replyToCmnd2)
                print("123" ,replyToCmnd)
                del to_send_gnd_cmd[uid]
            else:
                replyToCmnd2 = "noCommand2"
                replyToCmnd = (players,s_game_time,replyToCmnd2)
                
            
            

            if cmnd[2].split()[0]=="tkdmg":
                print(int(cmnd[2].split()[1])," shot ",int(cmnd[2].split()[2]))

                players[int(cmnd[2].split()[1])]["score"]+=50
                players[int(cmnd[2].split()[2])]["health"]-=10
                if players[int(cmnd[2].split()[2])]["health"]<10:
                    print(players[uid]["name"],"died")
                    replyToCmnd2 = "dead"
                    # conn.close()
            # print(replyToCmnd)
            replyToCmnd = (players,s_game_time,replyToCmnd2)
            conn.send(pickle.dumps(replyToCmnd))
        except Exception as e:
            print(e)
            break


        
    print("[DISCONNECTED]",name,"disconnected from the server")
    connected_clients-=1
    del players[uid]
    conn.close()


start_new_thread(save_playerInfo,())
while True:
    conn,addr = server_socket.accept()
    connected_clients+=1
    if connected_clients == 1 and game_state == "NOT RUNNING":
        game_state = "RUNNING"
        start_time=time.time()
        # start_new_thread( threaded_grenade_handler,())
        print("[LOG] Game Started")

    print("[NEW CONNECTION] Connected to: ",addr)
    start_new_thread(clientHandler,(conn,unique_id,addr))
    unique_id+=1