import pygame
import player
import grenade
class CameraGroup(pygame.sprite.Group):
    def __init__(self,screen):
        super().__init__()
        self.screen  = screen
        
        self.offset_vector = pygame.math.Vector2()
    
    #here target will be player[uid]
    def camera_target(self,target):
        self.offset_vector.x = target.rect.centerx - self.screen.get_size()[0]//2
        self.offset_vector.y = target.rect.centery - self.screen.get_size()[1]//2

    def draw_group_sprites(self,target):
        self.camera_target(target)
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset_vector
            self.screen.blit(sprite.image,offset_pos)

            if isinstance(sprite,player.Player):
                offset_pos = sprite.textRect.topleft - self.offset_vector
                self.screen.blit(sprite.text,offset_pos)
            if isinstance(sprite,grenade.Grenade) or isinstance(sprite,player.Player):
                # pygame.draw.rect(self.screen, "red",,  2)
                if hasattr(sprite,"hitbox"):
                    rec =  sprite.hitbox.copy()
                    rec.centerx = rec.centerx-self.offset_vector.x
                    rec.centery = rec.centery-self.offset_vector.y

                    pygame.draw.rect(self.screen, "red",rec,  2)