import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,char_type,name):
        super().__init__()
        self.image = pygame.image.load("topdown-shooter\\Vector Characters\\survivor 1\\g5972.png")
        self.image = pygame.transform.scale(self.image, (100,100))

        self.rect = self.image.get_rect(center =(pos_x,pos_y))

    
