import pygame

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,dirc,explode_time):
        super().__init__()
        
        self.image = pygame.image.load("ui\grenade.png")
        self.hitbox = self.image.get_rect().inflate((-40,0))
        self.rect = self.image.get_rect(center =(self.current_position.x,self.current_position.y))

    def update(self):
        pass
        
    