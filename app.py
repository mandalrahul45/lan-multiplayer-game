import datetime
import socket
import tkinter
from tkinter import simpledialog
from client import Connection
from _thread import *
from grenade import Grenade
import pygame
from player import Player
from pytmx.util_pygame import load_pygame
from camera import CameraGroup
import time
pygame.init()

#inititlized the screen and set caption:
WIDTH =1280
HEIGHT=768
dm = """
    
 __  __    __    ____  ____      _    _  ____  ____  _   _        ____  _  _  ___    __    __  __  ____ 
(  \/  )  /__\  (  _ \( ___)    ( \/\/ )(_  _)(_  _)( )_( )      (  _ \( \/ )/ __)  /__\  (  \/  )( ___)
 )    (  /(__)\  )(_) ))__)      )    (  _)(_   )(   ) _ (        )___/ \  /( (_-. /(__)\  )    (  )__) 
(_/\/\_)(__)(__)(____/(____)    (__/\__)(____) (__) (_) (_)      (__)   (__) \___/(__)(__)(_/\/\_)(____)

"""
print()
print()
print("|-------------------------------------------------------------------------------------------|")
print(dm)
MN = tkinter.Tk()
MN.withdraw()
NAME_ENTERED = simpledialog.askstring(title="Name?",
                                  prompt="What's your Name?:")
ADM_NO_ENTERED = simpledialog.askstring(title="Adm no>?",
                                  prompt="What's your Admission No.?:")
IP_ENTERED = simpledialog.askstring(title="SERVER IP?",
                                  prompt="ENTER SERVER IP?:")

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("LAN MULTIPLAYER") 
pygame.display.set_icon(pygame.image.load("ui\\icon.png"))

game_state=False
players={}
game_time=0
grenades=pygame.sprite.Group()

def changeTimeFormat(secs):
	mins = str(secs // 60)
	sec = str(secs % 60)
	if int(sec) < 10:
		sec = "0" + sec
	return mins + ":" + sec

def drawPlayers():
    pass

class Tile(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        # self.image = pygame.transform.scale(self.image,size)
        # self.image = pygame.transform.rotate(self.image,rttn)
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.copy()
tmx_data = load_pygame('Last Base\\Main Base.tmx')
camera_group = CameraGroup(screen)
collision_group = pygame.sprite.Group()
Tile(pos=(0,0),surf = pygame.image.load("Last Base\ground.png"),groups = camera_group)


for layer in tmx_data.visible_layers:
    if hasattr(layer,'data'):
        for x,y,surf in layer.tiles():
            pos = (x * 128, y * 128)
            if layer.name=="Walls" or layer.name=="Object layer 1" or layer.name=="Collidable":
                Tile(pos = pos, surf = surf,groups = [camera_group,collision_group])
            
for obj in tmx_data.objects:
    # print(dir(obj.image))

    pos = obj.x,obj.y
    
    # if obj.type in ('Building', 'Vegetation'):
    Tile(pos = pos, surf = obj.image, groups = camera_group)


def collision(position_vec,direction):
    
    orRect = pygame.Rect(position_vec.x-64,position_vec.y-64,128,128)
    plr_hitbox = pygame.Rect(position_vec.x-64,position_vec.y-64,128,128)
    for sprite in collision_group.sprites():
        if hasattr(sprite,"hitbox"):
            if sprite.hitbox.colliderect(plr_hitbox):
                if direction=="RIGHT":
                    plr_hitbox.right = sprite.hitbox.left
                elif direction =="LEFT":
                    plr_hitbox.left = sprite.hitbox.right

                elif direction=="UP":
                    plr_hitbox.top = sprite.hitbox.bottom
                elif direction =="DOWN":
                    plr_hitbox.bottom = sprite.hitbox.top
    return(pygame.math.Vector2(plr_hitbox.centerx,plr_hitbox.centery))

def display_leaderboard(uid):
    leaderboard_list = []
    for plr in players:
        leaderboard_list.append([players[plr]["name"], int(players[plr]["score"]) ])
        leaderboard_list.sort(key=lambda n:n[1],reverse=True)

    su = pygame.Surface((260,110+5))
    su.set_alpha(55)
    su.fill("black")
    screen.blit(su,(WIDTH-265,5))

    font = pygame.font.Font("ui\\Silkscreen-Regular.ttf",20)
    text = font.render("LEADERBOARD:", True,"black")
    textRect = text.get_rect(topleft=(WIDTH-205-60,10))
    screen.blit(text,textRect)

    

    
    font = pygame.font.Font("ui\\JetBrainsMono-Regular.ttf",25)
    if len(leaderboard_list)>0:
        medal_image = pygame.image.load("ui\\gold-medal.png")
        screen.blit(medal_image,(WIDTH-205-60,35))

        text = font.render((leaderboard_list[0][0])+" "+str(leaderboard_list[0][1]), True,"black")
        textRect = text.get_rect(topleft=(WIDTH-205-60+32,35))
        screen.blit(text,textRect)
    
    font = pygame.font.Font("ui\\JetBrainsMono-Regular.ttf",20)
    if len(leaderboard_list)>1:
        medal_image = pygame.image.load("ui\\silver-medal.png")
        screen.blit(medal_image,(WIDTH-205-60+5,35+32))

        text = font.render((leaderboard_list[1][0])+" "+str(leaderboard_list[1][1]), True,"black")
        textRect = text.get_rect(topleft=(WIDTH-205-60+33,35+28))
        screen.blit(text,textRect)
    if len(leaderboard_list)>2:
        medal_image = pygame.image.load("ui\\bronze-medal.png")
        screen.blit(medal_image,(WIDTH-205-60+5,35+32+28))

        text = font.render((leaderboard_list[2][0])+" "+str(leaderboard_list[2][1]), True,"black")
        textRect = text.get_rect(topleft=(WIDTH-205-60+33,35+28+24))
        screen.blit(text,textRect)

    #score_card
    scoreCard = pygame.image.load("ui\\score_card.png")
    screen.blit(scoreCard,(WIDTH//2 - 100,10))

    font = pygame.font.Font("ui\\Silkscreen-Regular.ttf",30)

    text = font.render(str(players[uid]["score"]), True,"black")
    textRect = text.get_rect(topleft=((WIDTH//2 - 100)+65,10))
    screen.blit(text,textRect)

datag = "cmd nothing"
cmd_from_server ="noCommand"
datagc = "cmd nothing"
def collidedWithGrenade(server,allPlrSprite,myPlayerSprite,uid):
    global grenades,datagc
    
    for plrSprite in allPlrSprite:
        for gds in grenades:
            # if gds.hitbox.colliderect(collision_group):
            #     gds.kill()
            #     break
            if int(plrSprite.pid)!=int(gds.deployer )and plrSprite.hitbox.colliderect(gds):
                # print("greande collided")
                # print(gds.deployer,plrSprite.pid)
                gds.kill()
                if plrSprite==myPlayerSprite:
                    #notify server of damage
                    # print("GOT HIT GO GIT GOT JIT")
                    datagc = "tkdmg "+str(gds.deployer) +" "+str(uid)
                    # return()


# def threaded_grenade_handler2(udp_socket,uid):
#     global cmd_from_server
#     cmd_from_server,address = udp_socket.recvfrom(1024*3)
# def threaded_grenade_handler(udp_socket,uid):
#     global datag,cmd_from_server
#     print("g1")   

#     while game_state:
#         print(datag)   
#         if datag!= "cmd nothing":
#             print("g3")   
#             udp_socket.sendto(datag.encode("utf-8"),("127.0.0.1",9696))
#             print(datag)
#             datag= "cmd nothing" 
        
        
               
def main(adm,name):
    global players,game_time,grenades,datag,game_state,datagc
    # print(1)
    server = Connection()
    # print(2)
    uid = server.connect(adm,name,IP_ENTERED)
    # print(3)
    reply_data = server.send("get",True)
    # print(4)
    # print("rep data: ",reply_data)
    players = reply_data[0]
    current_player = players[uid]
    direction_vector = pygame.math.Vector2()
    position_vector = pygame.math.Vector2(current_player["x"],current_player["y"])
    clock = pygame.time.Clock()
    
    

    game_state = True
    # udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    # udp_socket.bind(("127.0.0.1",9696))
    # start_new_thread(threaded_grenade_handler,(udp_socket,uid))
    # start_new_thread(threaded_grenade_handler2,(udp_socket,uid))

    ptime = time.time()
    prp = players[uid]["x"]
    direction = "RIGHT"

    while game_state:
        

        while True:
            clock.tick(30)
        
            current_player = players[uid]
            position_vector = pygame.math.Vector2(current_player["x"],current_player["y"])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            screen.fill("white")

            data ="get"
            keys = pygame.key.get_pressed()

            moved = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                direction_vector.x = 1
                direction_vector.y = 0

                # current_player["x"] = current_player["x"]+10
                direction = "RIGHT" 
                moved = True

            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                direction_vector.x = -1
                direction_vector.y = 0
                # current_player["x"] = current_player["x"]-10
                direction = "LEFT"
                moved = True
            # else:
            #     direction_vector.x=0

            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                direction_vector.y = -1
                direction_vector.x = 0
                # current_player["y"] = current_player["y"]-10
                direction = "UP"
                moved = True

            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                direction_vector.y = 1
                direction_vector.x = 0
                # current_player["y"] = current_player["y"]+10
                direction = "DOWN"
                moved = True
            else:
                direction_vector.x=0
                direction_vector.y=0

            
            if moved:
        
                position_vector = position_vector+(direction_vector*70)
                position_vector = collision(position_vector,direction)
                data = "move "+ str(int(position_vector.x)) + " " + str(int(position_vector.y))+" "+direction
            # print(direction_vector,position_vector)
            if keys[pygame.K_SPACE]:
                gxo = players[uid]["x"]
                gyo = players[uid]["y"]
                if direction=="RIGHT":
                    gxo+=30
                elif direction =="LEFT":
                    gxo-=30
                elif direction=="UP":
                    gyo-=30
                elif direction =="DOWN":
                    gyo+=30
                datag ="adGd "+str(gxo)+" "+str(gyo)+" "+players[uid]["direction_facing"]+" "+str(uid)
                # print("space pressed")
                
            data_recved= server.send((data,datag,datagc),True)
            players,game_time,cmd_from_server=data_recved
            datagc="nothing"
            datag="nothing"
            # print(data_recved)
            # print(" ")
            # print("dgd : ",cmd_from_server)
            if cmd_from_server !="noCommand":
                cmdlist = cmd_from_server.split()
                if cmdlist[0]=="dgd":
                    gnds_sprite = Grenade(int(cmdlist[1]),int(cmdlist[2]),cmdlist[3],cmdlist[4])
                    camera_group.add(gnds_sprite)
                    grenades.add(gnds_sprite)
                    # print("sprite created")
                
            if cmd_from_server =="dead":
                # print("I'M DEAD I'M DEAD I'M DEAD I'M DEAD")
                # dm =""" __     ______  _    _   _____  _          _   _ \n \ \   / / __ \| |  | | |  __ \(_)        | | | |\n  \ \_/ / |  | | |  | | | |  | |_  ___  __| | | |\n   \   /| |  | | |  | | | |  | | |/ _ \/ _` | | |\n    | | | |__| | |__| | | |__| | |  __/ (_| | |_|\n    |_|  \____/ \____/  |_____/|_|\___|\__,_| (_)\n                                                 """
                print()

                dm = """
                 _____   ___  ___  ___ _____   _____  _   _ ___________   _ 
                |  __ \ / _ \ |  \/  ||  ___| |  _  || | | |  ___| ___ \ | |
                | |  \// /_\ \| .  . || |__   | | | || | | | |__ | |_/ / | |
                | | __ |  _  || |\/| ||  __|  | | | || | | |  __||    /  | |
                | |_\ \| | | || |  | || |___  \ \_/ /\ \_/ / |___| |\ \  |_|
                 \____/\_| |_/\_|  |_/\____/   \___/  \___/\____/\_| \_| (_)

                """
                print(dm)
                print()
                print()
                print("|-------------------------------------------------------------------------------------------|")
                print("YOUR SCORE WAS: ",players[uid]["score"])
                print("|-------------------------------------------------------------------------------------------|")
                print()
                print()
                dm="""
                                
                 _   __                   _____           _ _ _                   __  
                | | / /                  /  ___|         (_) (_)               _  \ \ 
                | |/ /  ___  ___ _ __    \ `--. _ __ ___  _| |_ _ __   __ _   (_)  | |
                |    \ / _ \/ _ \ '_ \    `--. \ '_ ` _ \| | | | '_ \ / _` |       | |
                | |\  \  __/  __/ |_) |  /\__/ / | | | | | | | | | | | (_| |   _   | |
                \_| \_/\___|\___| .__/   \____/|_| |_| |_|_|_|_|_| |_|\__, |  (_)  | |
                                | |                                    __/ |      /_/ 
                                |_|                                   |___/           
                
                """
                print(dm)
                game_state = False
                break
            cmd_from_server ="noCommand"
            font = pygame.font.Font("ui\\Silkscreen-Regular.ttf",30)
            time_text = font.render(changeTimeFormat(int(game_time)), True,"black")
            textRect = time_text.get_rect()
            textRect.topleft = (8, 40)

            all_playersList_toRemove=[]
            current_player_sprite = ""
            #create all the sprites for the players
            for plr in players:
                # print(plr)
                plr_sprite = Player(players[plr]["x"],players[plr]["y"],players[plr]["characterType"],players[plr]["name"],players[plr]["direction_facing"],True if int(plr)==int(uid) else False,int(plr))

                if plr==uid:
                    current_player_sprite = plr_sprite

                all_playersList_toRemove.append(plr_sprite)
                collision_group.add(plr_sprite)
                camera_group.add(plr_sprite)

            
            
            # print(5)
            
            
            
            

            collidedWithGrenade(server,all_playersList_toRemove,current_player_sprite,uid)
            # print(health_state)
            # if health_state =="dead":
            #     print("player died")
            #     game_state=False
            #     break
            camera_group.draw_group_sprites(current_player_sprite)
            camera_group.remove(all_playersList_toRemove)
            collision_group.remove(all_playersList_toRemove)
            # camera_group.remove(all_grenadesSprites_toRemove)
            camera_group.update()
            

            clock_image = pygame.image.load("ui\\clock.png")
            
            su = pygame.Surface((200,110))
            su.set_alpha(55)
            su.fill("black")
            screen.blit(su,(5,5))

            screen.blit(clock_image,textRect)
            textRect.x +=36
            screen.blit(time_text,textRect)
            ## health bar
            heart_image = pygame.image.load("ui\\heart 1.png")
            # heart_image = pygame.transform.scale(heart_image,(30,30))
            screen.blit(heart_image,(8,8))

            # gd = pygame.image.load("ui\grenade.png")
            # gd_small = pygame.image.load("ui\\grenade small.png")
            
            hbar= pygame.Surface((150,10))
            hbar.fill("white")
            screen.blit(hbar,(45,17))

            hbar= pygame.Surface((max(0,int(150*(players[uid]["health"]/500))),10))
            hbar.fill((84, 180, 53))
            
            screen.blit(hbar,(45,17))

            # screen.blit(gd_small,(5,79))

            # gc = font.render(str(players[uid]["grenade_count"]), True,"black")
            # textRect = gc.get_rect()
            # textRect.topleft = (43, 79)
            # screen.blit(gc,textRect)
            display_leaderboard(uid)
            pygame.display.update()
            break
        # print("GAME ENDED")
        if not game_state:
            break
    # server.disconnect()
    # pygame.quit()
    # quit()


    
main(ADM_NO_ENTERED,NAME_ENTERED)
# main(123,"Rahul Mandal")