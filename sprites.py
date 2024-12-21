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
        self.distance = 0 # The distance from the player to the turret's muzzle
        self.angle = 0
        self.firing_frame_duration = 200  # Duration for each firing animation frame in milliseconds
        super().__init__(groups)        
        
        # Turret frames
        self.turret_frames = [
            pygame.image.load(join('images', 'turret', f'player_{i}.png')).convert_alpha()
            for i in range(5)
        ]
        self.turret_frame_index = 0
        self.turret_timer = pygame.time.get_ticks()
        self.turret_frame_duration = 100  # Time per turret frame (in milliseconds)

        # Firing frames
        self.firing_frames = [
            pygame.image.load(join('images', 'fire', f'player_{i}.png')).convert_alpha()
            for i in range(3)
        ]
        self.firing_frame_index = 0
        self.firing = False
        self.firing_timer = 0
        self.firing_frame_duration = 100  # Time per firing frame

        # Image and rect
        self.image = self.turret_frames[0]
        self.rect = self.image.get_frect(center=player.rect.center)

    
    def get_direction(self):
        """Calculate the direction vector from the player to the mouse position."""
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)  # Assuming the player is centered
        direction = mouse_pos - player_pos
        self.angle = -degrees(atan2(direction.y, direction.x)) + 90
        
    def rotate_turret(self):        
        # Rotate turret animation frame
        current_frame = self.turret_frames[self.turret_frame_index]
        rotated_image = pygame.transform.rotozoom(current_frame, self.angle, 1)
        self.image = rotated_image
        self.rect = self.image.get_frect(center=self.player.rect.center)
    
    def start_firing(self):
        """Start the firing animation."""
        self.firing = True
        self.firing_timer = pygame.time.get_ticks()
        self.firing_frame_index = 0
        
    def update(self, _):
        """Update the turret's rotation, firing animation, and turret animation."""
        self.get_direction()

        if self.firing:
            current_time = pygame.time.get_ticks()

            # Update firing animation frame
            if current_time - self.firing_timer >= self.firing_frame_duration * (self.firing_frame_index + 1):
                self.firing_frame_index += 1
                if self.firing_frame_index >= len(self.firing_frames):
                    self.firing_frame_index = 0
                    self.firing = False  # Stop firing animation once it completes

            # Update turret animation frame
            if current_time - self.firing_timer >= self.firing_frame_duration * (self.turret_frame_index + 1):
                self.turret_frame_index += 1
                if self.turret_frame_index >= len(self.turret_frames):
                    self.turret_frame_index = 0  # Reset to first frame when animation ends

        else:
            # If not firing, reset the turret to its default frame
            self.turret_frame_index = 0

        # Handle firing animation offset and rotation
        if self.firing:
            firing_frame = self.firing_frames[self.firing_frame_index]
            rotated_firing_frame = pygame.transform.rotozoom(firing_frame, self.angle, 1)
            firing_offset = pygame.Vector2(0, 0).rotate(-self.angle)
            firing_pos = pygame.Vector2(self.rect.center) + firing_offset
            self.firing_rect = rotated_firing_frame.get_frect(center=firing_pos)

        # Always rotate the turret, regardless of firing
        self.rotate_turret()
                    
    def draw(self, surface, center):
        # Calculate offset
        offset = pygame.Vector2(center) - (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

        # Draw the turret
        shifted_rect = self.rect.move(-offset.x, -offset.y)
        surface.blit(self.image, shifted_rect.topleft)

        # Draw firing animation
        if self.firing:
            firing_frame = self.firing_frames[self.firing_frame_index]
            rotated_firing_frame = pygame.transform.rotozoom(firing_frame, self.angle, 1)
            firing_rect = rotated_firing_frame.get_frect(center=shifted_rect.center)
            surface.blit(rotated_firing_frame, firing_rect.topleft)

class Shell(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups, x_offset):
        super().__init__(groups)
        self.original_image = surf
        
        # Create a glowing effect by scaling up and brightening
        # First, create a larger version for the glow
        glow_size = (surf.get_width() * 1.5, surf.get_height() * 1.5)
        self.glow_image = pygame.transform.scale(surf, glow_size)
        
        # Brighten the glow image
        bright_surf = self.glow_image.copy()
        bright_surf.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
        self.glow_image = bright_surf
        
        # Brighten the main image
        self.original_image = surf.copy()
        self.original_image.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_ADD)
        
        self.image = self.original_image
        self.rect = self.image.get_frect(center = pos)
        self.glow_rect = self.glow_image.get_frect(center = pos)
        
        # movement
        self.pos = pygame.Vector2(pos)
        self.direction = direction
        self.speed = 400
        self.x_offset = x_offset
        self.z = 4
        
        # Calculate angle of the shell based on the direction vector
        self.angle = -degrees(atan2(self.direction.y, self.direction.x)) + 270
        self.rotate_shell()

    def rotate_shell(self):
        """Rotate both the shell image and its glow effect."""
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        self.glow_image_rotated = pygame.transform.rotozoom(self.glow_image, self.angle, 1)
        
        # Update both rectangles
        old_center = self.rect.center
        self.rect = self.image.get_frect(center=old_center)
        self.glow_rect = self.glow_image_rotated.get_frect(center=old_center)
        
    def draw(self, surface, offset):
        """Custom draw method to handle the glow effect."""
        # Draw glow first
        glow_pos = self.glow_rect.topleft + offset
        surface.blit(self.glow_image_rotated, glow_pos)
        
        # Draw main shell
        shell_pos = self.rect.topleft + offset
        surface.blit(self.image, shell_pos)
        
    def update(self, dt):
        # Update position
        movement = self.direction * self.speed * dt
        self.pos += movement
        self.rect.center = self.pos
        self.glow_rect.center = self.pos
        self.rotate_shell()