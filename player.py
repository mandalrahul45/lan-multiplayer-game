import pygame

CHARACTERS={
    "Survivor1":{}
}

class Player(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,char_type,name,direction_facing):
        super().__init__()
        self.image = pygame.image.load("topdown-shooter\\Vector Characters\\survivor 1\\g1076.png")
        self.image = pygame.transform.scale(self.image, (150,150))
        rotaion_values={"UP":90,"DOWN":-90,"LEFT":-180,"RIGHT":0}
        self.image = pygame.transform.rotate(self.image, rotaion_values[direction_facing])
        self.rect = self.image.get_rect(center =(pos_x,pos_y))

        self.hitbox = self.rect.copy()
        
    

    
