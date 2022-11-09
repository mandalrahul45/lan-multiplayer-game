import pygame

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direc,explode_time):
        super().__init__()
        self.explode_time =explode_time
        self.image = pygame.image.load("ui\grenade.png")
        self.x=x
        self.y=y
        self.hitbox = self.image.get_rect().inflate((-40,0))
        self.rect = self.image.get_rect(center =(x,y))
        self.direc = direc
    def update(self,game_time):
        if self.direc =="RIGHT":
            self.x+=20
            self.rect.centerx+=20
        if game_time == self.explode_time:
            self.kill()
        pass
        
    