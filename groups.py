from settings import *

class AllSprites(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        
    def draw(self, target_pos):
        # player camera
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        
        # Get all sprites sorted by layer only
        for sprite in self.sprites():
            if hasattr(sprite, 'z'):
                self.change_layer(sprite, sprite.z)
        
        # Draw sprites based on layer order
        for layer in self.layers():
            for sprite in self.get_sprites_from_layer(layer):
                offset_pos = sprite.rect.topleft + self.offset
                self.display_surface.blit(sprite.image, offset_pos)