import pygame

CHARACTERS={
    "Survivor1":{}
}

class Player(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,char_type,name,direction_facing,myself,uid):
        self.pid =uid
        super().__init__()
        self.image = pygame.image.load("topdown-shooter\\Vector Characters\\survivor 1\\g1076.png")
        # self.image = pygame.transform.scale(self.image, (150,150))
        rotaion_values={"UP":90,"DOWN":-90,"LEFT":-180,"RIGHT":0}
        self.image = pygame.transform.rotate(self.image, rotaion_values[direction_facing])
        self.rect = self.image.get_rect(center =(pos_x,pos_y))

        self.hitbox = self.rect.copy().inflate((-10,0))

        #name tag
        font = pygame.font.Font("ui\Silkscreen-Regular.ttf",20)
        
        self.text = font.render(name, True,"black" if myself else "red")
        if direction_facing=="UP":
            self.textRect = self.text.get_rect(midtop = self.rect.midbottom)
        else:
            self.textRect = self.text.get_rect(midbottom = self.rect.midtop)
        
        
    

    
