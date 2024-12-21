from settings import *
from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, hitbox_inflation=(0, 0)):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        
        # Apply hitbox inflation: shrinking by default with negative values
        self.hitbox_rect = self.rect.inflate(*hitbox_inflation)  # Modify hitbox size
        
        # Make sure to set up the groups
        self.groups = groups
        
    def update(self, dt):
        # Update logic for movement, collision, etc.
        pass

    def draw(self, surface, offset=(0, 0)):
        """Draw the sprite and optionally the hitbox for debugging"""
        surface.blit(self.image, self.rect.topleft + pygame.Vector2(offset))
        
        # Debug print to check the size of the hitbox
        print(f"Hitbox size: {self.hitbox_rect.size}")
        
        pygame.draw.rect(surface, (255, 0, 0), self.hitbox_rect.topleft + pygame.Vector2(offset), 2)
        
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
    def __init__(self, surf, pos, direction, groups, x_offset, collision_sprites, hitbox_inflation=(-110, -110)):
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
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(*hitbox_inflation)  # Adjusted hitbox
        
        # movement
        self.pos = pygame.Vector2(pos)
        self.direction = direction
        self.speed = 400
        self.x_offset = x_offset
        self.z = 4
        self.collision_sprites = collision_sprites
        
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
        old_pos = self.pos.copy() # savel the old position for impact animation
        self.pos += movement
        self.rect.center = self.pos
        self.hitbox_rect.center = self.pos
        self.rotate_shell()

        # Check collisions using the adjusted hitbox_rect
        for sprite in self.collision_sprites:
            if self.hitbox_rect.colliderect(sprite.hitbox_rect):  # Use hitbox_rect instead of rect
                # Trigger impact animation at the collision point
                mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
                impact_pos = self.hitbox_rect.center  # Position the impact animation at the collision point
                ImpactAnimation(impact_pos, self.groups(), mouse_pos, self.direction)  # Trigger the impact animation with the mouse position
                self.kill()  # Destroy the shell on collision

        # # Check collisions using the adjusted hitbox_rect
        # for sprite in self.collision_sprites:
        #     if self.hitbox_rect.colliderect(sprite.hitbox_rect):  # Use hitbox_rect instead of rect
        #         self.kill()  # Destroy the shell on collision

class ImpactAnimation(pygame.sprite.Sprite):
    def __init__(self, position, groups, mouse_pos, direction):
        super().__init__(groups)
        self.frames = [
            pygame.image.load(join('images', 'impact', f'{i}.png')).convert_alpha() for i in range(4)
        ]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_frect(center=position)
        self.duration = 100  # Duration per frame (in milliseconds)
        self.timer = pygame.time.get_ticks()  # Track time to change frames
        
        # Use the direction vector of the shell to calculate the angle
        self.angle = self.calculate_angle(position, mouse_pos, direction)  # Pass direction vector
        self.rotate_image()  # Rotate the impact image to the correct angle
    
    def calculate_angle(self, position, mouse_pos, direction):
        """Calculate the angle between the impact position, mouse position, and the direction vector."""
        # Calculate direction vector from the position to the mouse position
        dx = mouse_pos[0] - position[0]
        dy = mouse_pos[1] - position[1]
        
        # Calculate the angle of the direction vector for the player
        direction_angle = -degrees(atan2(direction.y, direction.x)) + 90
        
        return direction_angle  # Use direction_angle directly for the top of the impact image
    
    def rotate_image(self):
        """Rotate the impact image to face the player's direction."""
        self.image = pygame.transform.rotozoom(self.frames[self.current_frame], self.angle, 1)
        self.rect = self.image.get_frect(center=self.rect.center)  # Keep the position centered
    
    def update(self, dt=None):  # Add dt argument to avoid the TypeError
        """Update the impact animation frame"""
        current_time = pygame.time.get_ticks()
        if current_time - self.timer >= self.duration:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill()  # Remove the animation after the last frame
            else:
                self.image = self.frames[self.current_frame]
                self.rotate_image()  # Rotate to the current frame's angle
                self.rect = self.image.get_frect(center=self.rect.center)  # Keep the position centered
                self.timer = current_time  # Reset the timer for next frame