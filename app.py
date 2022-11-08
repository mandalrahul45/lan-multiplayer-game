import datetime
import tkinter
from tkinter import simpledialog
from client import Connection
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

players={}
game_time=0
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
    global players,game_time

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
                position_vector = position_vector+(direction_vector*10)
                position_vector = collision(position_vector,direction)
                data = "move "+ str(int(position_vector.x)) + " " + str(int(position_vector.y))+" "+direction
            # print(direction_vector,position_vector)
            players,game_time = server.send(data)
            

            font = pygame.font.SysFont("arial",55)
            time_text = font.render(changeTimeFormat(int(game_time)), True,"black")
            textRect = time_text.get_rect()
            textRect.topleft = (10, 10)

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

            camera_group.draw_group_sprites(current_player_sprite)
            camera_group.remove(all_playersList_toRemove)
            camera_group.update()
            screen.blit(time_text,textRect)
            pygame.display.update()

    server.disconnect()
    pygame.quit()
    quit()


    
# main(ADM_NO_ENTERED,NAME_ENTERED)
main(123,"rahul")