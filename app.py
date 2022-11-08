import datetime
import tkinter
from tkinter import simpledialog
from client import Connection
from grenade import Grenade
import pygame
from player import Player
from pytmx.util_pygame import load_pygame
from camera import CameraGroup
pygame.init()

#inititlized the screen and set caption:
WIDTH =1280
HEIGHT=768

# MN = tkinter.Tk()
# MN.withdraw()
# NAME_ENTERED = simpledialog.askstring(title="Name?",
#                                   prompt="What's your Name?:")
# ADM_NO_ENTERED = simpledialog.askstring(title="Adm no>?",
#                                   prompt="What's your Admission No.?:")

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("LAN MULTIPLAYER") 
pygame.display.set_icon(pygame.image.load("ui\icon.png"))

players={}
game_time=0
grenades={}

def changeTimeFormat(secs):
	mins = str(secs // 60)
	sec = str(secs % 60)
	if int(sec) < 10:
		sec = "0" + sec
	return mins + ":" + sec

def drawPlayers():
    pass

class Tile(pygame.sprite.Sprite):
    def __init__(self,size,pos,surf,rttn,groups):
        super().__init__(groups)
        self.image = surf
        self.image = pygame.transform.scale(self.image,size)
        self.image = pygame.transform.rotate(self.image,rttn)
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.copy()
tmx_data = load_pygame('hello\\newmap.tmx')
camera_group = CameraGroup(screen)
collision_group = pygame.sprite.Group()


for layer in tmx_data.visible_layers:
    if hasattr(layer,'data'):
        for x,y,surf in layer.tiles():
            pos = (x * 128, y * 128)
            if layer.name=="wall":
                Tile(size=(128,128),pos = pos, surf = surf,rttn= 0,groups = [camera_group,collision_group])
            else:
                Tile(size=(128,128),pos = pos, surf = surf,rttn= 0,groups = camera_group)
for obj in tmx_data.objects:
    # print(dir(obj.image))

    pos = obj.x,obj.y
    
    # if obj.type in ('Building', 'Vegetation'):
    Tile(size=(obj.width,obj.height),pos = pos, surf = obj.image,rttn = obj.rotation, groups = camera_group)


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

def main(adm,name):
    global players,game_time,grenades

    server = Connection()
    uid = server.connect(adm,name)

    reply_data = server.send("get")
    players = reply_data[0]
    current_player = players[uid]
    direction_vector = pygame.math.Vector2()
    position_vector = pygame.math.Vector2(current_player["x"],current_player["y"])
    clock = pygame.time.Clock()

    game_state = True
    while game_state:
        clock.tick(30)
        current_player = players[uid]
        position_vector = pygame.math.Vector2(current_player["x"],current_player["y"])

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            screen.fill("white")

            data ="get"
            keys = pygame.key.get_pressed()

            direction = ""
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
                position_vector = position_vector+(direction_vector*25)
                position_vector = collision(position_vector,direction)
                data = "move "+ str(int(position_vector.x)) + " " + str(int(position_vector.y))+" "+direction
            # print(direction_vector,position_vector)
            players,game_time,grenades = server.send(data)
            

            font = pygame.font.SysFont("arial",30)
            time_text = font.render(changeTimeFormat(int(game_time)), True,"black")
            textRect = time_text.get_rect()
            textRect.topleft = (8, 40)

            all_playersList_toRemove=[]
            current_player_sprite = ""
            #create all the sprites for the players
            for plr in players:
                # print(plr)
                plr_sprite = Player(players[plr]["x"],players[plr]["y"],players[plr]["characterType"],players[plr]["name"],players[plr]["direction_facing"])

                if plr==uid:
                    current_player_sprite = plr_sprite

                all_playersList_toRemove.append(plr_sprite)

                camera_group.add(plr_sprite)


            if keys[pygame.K_SPACE]:
                gxo = players[uid]["x"]
                gyo = players[uid]["y"]
                if direction=="RIGHT":
                    gxo+=50
                elif direction =="LEFT":
                    gxo-=50
                elif direction=="UP":
                    gyo-=50
                elif direction =="DOWN":
                    gyo+=50
                datag ="addGrenade "+str(gxo)+" "+str(gyo)+" "+str(gxo*(position_vector.x+200))+" "+str(gyo*(position_vector.x+200))+" "+str(gxo)+" "+str(gyo)+" active "+str(position_vector.x)+" "+str(position_vector.y)
                players,game_time,grenades = server.send(datag)
            
            
            all_grenadesSprites_toRemove=[]
            #create all the sprites for the grenades
            for gds in grenades:
                print(grenades[gds])
                origin_vector = pygame.math.Vector2(int(grenades[gds]["origin_x"]),int(grenades[gds]["origin_y"]))
                destination_vector = pygame.math.Vector2(int(float(grenades[gds]["dest_x"])),int(float(grenades[gds]["dest_y"])))
                current_position_vector = pygame.math.Vector2(int(float(grenades[gds]["pos_x"])),int(float(grenades[gds]["pos_y"])))
                additive_vec = pygame.math.Vector2(int(float(grenades[gds]["add_vec_x"])),int(float(grenades[gds]["add_vec_y"])))

                gnds_sprite = Grenade(origin_vector,destination_vector,current_position_vector,additive_vec,(True if int(grenades[gds]["deployer_id"])==uid else False ),grenades[gds]["state"])

                all_grenadesSprites_toRemove.append(gnds_sprite)

                camera_group.add(gnds_sprite)
            


            camera_group.draw_group_sprites(current_player_sprite)
            camera_group.remove(all_playersList_toRemove)
            camera_group.remove(all_grenadesSprites_toRemove)
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

            gd = pygame.image.load("ui\grenade.png")
            gd_small = pygame.image.load("ui\grenade small.png")
            
            hbar= pygame.Surface((150,10))
            hbar.fill("white")
            screen.blit(hbar,(45,17))

            hbar= pygame.Surface((int(150*(players[uid]["health"]/100)),10))
            hbar.fill((84, 180, 53))
            
            screen.blit(hbar,(45,17))

            screen.blit(gd_small,(5,79))

            gc = font.render(str(players[uid]["grenade_count"]), True,"black")
            textRect = gc.get_rect()
            textRect.topleft = (43, 79)
            screen.blit(gc,textRect)
            pygame.display.update()

    server.disconnect()
    pygame.quit()
    quit()


    
# main(ADM_NO_ENTERED,NAME_ENTERED)
main(123,"rahul")