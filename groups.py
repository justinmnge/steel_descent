from settings import *
from sprites import Shell

class AllSprites(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        
    def custom_draw(self, target_pos):
        # player camera
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        
        # Draw sprites based on layer order
        for layer in self.layers():
            for sprite in self.get_sprites_from_layer(layer):
                if isinstance(sprite, Shell):
                    # Use custom draw method for shells
                    sprite.draw(self.display_surface, self.offset)
                else:
                    # Normal sprite drawing
                    offset_pos = sprite.rect.topleft + self.offset
                    self.display_surface.blit(sprite.image, offset_pos)