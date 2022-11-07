import datetime

from client import Connection
import pygame
from player import Player
from pytmx.util_pygame import load_pygame
from camera import CameraGroup
pygame.init()

#inititlized the screen and set caption:
WIDTH =1280
HEIGHT=768
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
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        # self.image = pygame.transform.scale(self.image,(100,100))
        self.rect = self.image.get_rect(topleft = pos)

tmx_data = load_pygame('Tiled 2\\\\newmap.tmx')
camera_group = CameraGroup(screen)

for layer in tmx_data.visible_layers:
    if hasattr(layer,'data'):
        for x,y,surf in layer.tiles():
            pos = (x * 128, y * 128)
            Tile(pos = pos, surf = surf, groups = camera_group)
 
for obj in tmx_data.objects:
    pos = obj.x,obj.y
    if obj.type in ('Building', 'Vegetation'):
        Tile(pos = pos, surf = obj.image, groups = camera_group)


def main(adm,name):
    global players,game_time

    server = Connection()
    uid = server.connect(adm,name)

    reply_data = server.send("get")
    players = reply_data[0]
    current_player = players[uid]

    clock = pygame.time.Clock()

    game_state = True
    while game_state:
        clock.tick(30)
        current_player = players[uid]
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
                current_player["x"] = current_player["x"]+10
                direction = "RIGHT"
                moved = True

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                current_player["x"] = current_player["x"]-10
                direction = "LEFT"
                moved = True

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                current_player["y"] = current_player["y"]-10
                direction = "UP"
                moved = True

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                current_player["y"] = current_player["y"]+10
                direction = "DOWN"
                moved = True
            if moved:
                data = "move "+ str(current_player["x"]) + " " + str(current_player["y"])+" "+direction

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
    
main(123,"Rahul")