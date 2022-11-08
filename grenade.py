import pygame

class Grenade(pygame.sprite.Sprite):
    def __init__(self,origin_vector,destination_vector,current_position,addititve_vec,self_deployer,state):
        super().__init__()
        self.origin = origin_vector
        self.dest = destination_vector
        self.current_position = current_position
        self.state = state
        self.additive =addititve_vec
        self.self_deployer=self_deployer
        self.image = pygame.image.load("ui\grenade.png")
        self.hitbox = self.image.get_rect().inflate((-40,0))
        self.rect = self.image.get_rect(center =(self.current_position.x,self.current_position.y))

    def update(self):
        if(self.self_deployer and self.current_position!=self.dest):
            self.current_position+=self.additive*10
        
    