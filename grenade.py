import pygame

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direc,deployer):
        super().__init__()
        dist_to_explode =650
        self.deployer =deployer
        cases={
            "RIGHT":{"x":x+dist_to_explode,"y":y},
            "LEFT":{"x":x-dist_to_explode,"y":y},
            "DOWN":{"x":x,"y":y+dist_to_explode},
            "UP":{"x":x,"y":y-dist_to_explode}
        }
        self.explode_posx = cases[direc]["x"]
        self.explode_posy = cases[direc]["y"]

        self.image = pygame.image.load(f"ui\\rocket-{direc.lower()}.png")
        self.x=x
        self.y=y
        self.rect = self.image.get_rect(center =(x,y))
        self.hitbox = self.rect.copy().inflate((-50,-50))
        if direc == "RIGHT" or direc == "LEFT": 
            self.hitbox.centerx=x+30
            self.hitbox.width,self.hitbox.height=self.hitbox.height,self.hitbox.width
        else:
            self.hitbox.centery=y-30

        
        self.direc = direc
    def update(self):
        if self.direc =="RIGHT":
            self.x+=70
            self.rect.centerx+=70
            self.hitbox.centerx = self.rect.centerx+30

        elif self.direc =="LEFT":
            self.x-=70
            self.rect.centerx-=70
            self.hitbox.centerx = self.rect.centerx-30


        elif self.direc =="UP":
            self.y-=70
            self.rect.centery-=70
            self.hitbox.centery = self.rect.centery-30

        elif self.direc =="DOWN":
            self.y+=70
            self.rect.centery+=70
            self.hitbox.centery = self.rect.centery+30

        # self.hitbox.center = self.rect.center
        if self.x>=self.explode_posx and self.y>=self.explode_posy and (self.direc == "RIGHT" or self.direc =="DOWN"):
            #kill any nearby player
            self.kill()
        elif self.x<=self.explode_posx and self.y<=self.explode_posy and (self.direc == "LEFT" or self.direc =="UP"):
            #kill any nearby player
            self.kill()
        #or if the grenade collides with something
    