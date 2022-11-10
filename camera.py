import pygame
import player
import grenade
class CameraGroup(pygame.sprite.Group):
    def __init__(self,screen):
        super().__init__()
        self.screen  = screen
        
        self.offset_vector = pygame.math.Vector2()

        self.half_w = self.screen.get_size()[0] // 2
        self.half_h = self.screen.get_size()[1] // 2

        # camera speed
        self.keyboard_speed = 5
        self.mouse_speed = 0.2

        # zoom 
        self.zoom_scale = 1
        self.internal_surf_size = (2500,2500)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center = (self.half_w,self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h
    
    #here target will be player[uid]
    def zoom_keyboard_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.zoom_scale += 0.1
        if keys[pygame.K_e]:
            self.zoom_scale = max(self.zoom_scale-0.1,0.3)
        print(self.zoom_scale)

    def camera_target(self,target):
        self.offset_vector.x = target.rect.centerx - self.screen.get_size()[0]//2
        self.offset_vector.y = target.rect.centery - self.screen.get_size()[1]//2

    def draw_group_sprites(self,target):

        self.zoom_keyboard_control()
        self.internal_surf.fill('white')
        self.camera_target(target)
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset_vector + self.internal_offset
            self.internal_surf.blit(sprite.image,offset_pos)

            if isinstance(sprite,player.Player):
                offset_pos = sprite.textRect.topleft - self.offset_vector + self.internal_offset
                self.internal_surf.blit(sprite.text,offset_pos)
            # if isinstance(sprite,grenade.Grenade) or isinstance(sprite,player.Player):
            #     # pygame.draw.rect(self.screen, "red",,  2)
            #     if hasattr(sprite,"hitbox"):
            #         rec =  sprite.hitbox.copy()
            #         rec.centerx = rec.centerx-self.offset_vector.x
            #         rec.centery = rec.centery-self.offset_vector.y

                    # pygame.draw.rect(self.internal_surf, "red",rec,  2)

        scaled_surf = pygame.transform.scale(self.internal_surf,self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center = (self.half_w,self.half_h))
        self.screen.blit(scaled_surf,scaled_rect)