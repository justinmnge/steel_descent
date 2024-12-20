from settings import *
from os.path import join
from os import walk

class Player(pygame.sprite.Sprite):
    def __init__(self,pos, groups, collision_sprites):
        super().__init__(groups)
        self.rotation = 0
        
        # hull
        self.load_images()
        self.state, self.frame_index = 'idle', 0
        self.animation_speed = 5
        self.rect = self.frames['idle'][0].get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-80, -70)
        
        # movement
        self.direction = pygame.Vector2()
        self.speed = 250
        self.rotation_speed = 180
        self.collision_sprites = collision_sprites
        self.move_forward = 0
    
    def load_images(self):
        # idle animation for player
        self.frames = {'idle': []}
        self.rotated_frames = {'idle': {}}
        
        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)
        
       # Initialize rotation 0 with original frames
        for state in self.frames.keys():
            self.rotated_frames[state] = {0: self.frames[state].copy()}  # Initialize angle 0 with copy of original frames
    
    def get_rotated_frame(self, state, frame_index, angle):
        # Round angle to nearest 5 degrees to reduce memory usage
        angle = round(angle / 5) * 5
        angle %= 360
        
        # If we haven't cached this rotation angle yet, create it
        if angle not in self.rotated_frames[state]:
            self.rotated_frames[state][angle] = []
            for frame in self.frames[state]:
                rotated = pygame.transform.rotate(frame, angle)
                self.rotated_frames[state][angle].append(rotated)
        
        # Make sure we wrap around if frame_index exceeds number of frames
        frame_index = frame_index % len(self.frames[state])
        
        # Return the appropriate rotated frame
        return self.rotated_frames[state][angle][frame_index]
       
    def input(self, dt):
        keys = pygame.key.get_pressed()

        # Rotation
        if keys[pygame.K_a]:
            self.rotation += self.rotation_speed * dt
        if keys[pygame.K_d]:
            self.rotation -= self.rotation_speed * dt
        
        self.rotation %= 360
        self.move_forward = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
    
    def move(self, dt):
        if self.move_forward != 0:
            # Calculate the movement vector based on rotation
            movement_vector = pygame.Vector2(0, -1).rotate(-self.rotation) * self.move_forward
            
            # Store intended movement for collision checking
            intended_x = self.rect.x + movement_vector.x * self.speed * dt
            intended_y = self.rect.y + movement_vector.y * self.speed * dt
            
            # Move horizontally and check collision
            old_x = self.rect.x
            old_hitbox_x = self.hitbox_rect.x
            self.rect.x = intended_x
            self.hitbox_rect.x = self.rect.centerx - self.hitbox_rect.width / 2
            if self.check_collisions():
                self.rect.x = old_x
                self.hitbox_rect.x = old_hitbox_x
            
            # Move vertically and check collision
            old_y = self.rect.y
            old_hitbox_y = self.hitbox_rect.y
            self.rect.y = intended_y
            self.hitbox_rect.y = self.rect.centery - self.hitbox_rect.height / 2
            if self.check_collisions():
                self.rect.y = old_y
                self.hitbox_rect.y = old_hitbox_y
    
    def check_collisions(self):                
        """Returns True if there is a collision with any sprite"""
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                return True
        return False
    
    def animate(self, dt):
        # update animation frame
        self.frame_index += self.animation_speed * dt
        frame_index = int(self.frame_index)
        
        # get correctly rotated frame for current animation frame
        self.image = self.get_rotated_frame(self.state, frame_index, self.rotation)
        
        # Update rect position while maintaining center
        center = self.rect.center
        self.rect = self.image.get_frect()
        self.rect.center = center
        
        # Update hitbox position
        self.hitbox_rect.center = self.rect.center
    
    def update(self, dt):
        self.input(dt)
        self.move(dt)
        self.animate(dt)