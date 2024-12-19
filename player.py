from settings import *
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self,pos, groups):
        super().__init__(groups)
        self.rotation = 0
        
        # hull
        self.original_image = pygame.image.load(join('images', 'player', '0.png')).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_frect(topleft = pos)
        
        # movement
        self.direction = pygame.Vector2()
        self.speed = 250
        self.rotation_speed = 180
        
    def input(self, dt):
        keys = pygame.key.get_pressed()

        # Rotation
        if keys[pygame.K_a]:
            self.rotation += self.rotation_speed * dt
        if keys[pygame.K_d]:
            self.rotation -= self.rotation_speed * dt
            
        self.rotation %= 360
        
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_frect(center = self.rect.center)
            
        self.move_forward = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
    
    def move(self, dt):
        if self.move_forward != 0:
            movement_vector = pygame.Vector2(0, -1).rotate(-self.rotation) * self.move_forward
            self.rect.center += movement_vector * self.speed * dt
    
    def update(self, dt):
        self.input(dt)
        self.move(dt)