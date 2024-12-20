from settings import *
from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        
class Turret(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # player connection
        self.player = player
        self.distance = 0
        self.angle = 0
        self.player_direction = pygame.Vector2()
        
        # sprite setup
        super().__init__(groups)
        self.original_image = pygame.image.load(join('images', 'turret', 'player_0.png'))
        self.image = self.original_image
        self.rect = self.image.get_frect(center = player.rect.center)
    
    def get_direction(self):
        """Calculate the direction vector from the player to the mouse position."""
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)  # Assuming the player is centered
        self.player_direction = mouse_pos - player_pos
        self.angle = -degrees(atan2(self.player_direction.y, self.player_direction.x)) + 90 # Calculate the angle
        
    def rotate_turret(self):
        """Rotate the turret image to face the direction of the mouse."""
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        # Calculate offset position based on angle and distance
        offset = pygame.Vector2(self.distance, 0).rotate(-self.angle)
        player_center = pygame.Vector2(self.player.rect.center)
        new_pos = player_center + offset
        self.rect = self.image.get_frect(center=new_pos)  # Position relative to player with offset
        
    def update(self, _):
        """Update the turret's position and rotation."""
        self.get_direction()
        self.rotate_turret()
        
        # Update position to stay aligned with player
        self.rect.center = (
            self.player.rect.centerx,
            self.player.rect.centery - self.distance  # Keep same vertical offset
        )

class Shell(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        
        # movement
        self.pos = pygame.Vector2(pos)
        self.direction = direction
        self.speed = 400
        
        self.z = 4
        print(f'Shell initialized at: {self.pos}')
        
    def update(self, dt):
        # Update position
        old_pos = pygame.Vector2(self.pos)
        movement = self.direction * self.speed * dt
        self.pos += movement
        self.rect.center = self.pos