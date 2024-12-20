from settings import *
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self,pos, groups, collision_sprites):
        super().__init__(groups)
        self.rotation = 0
        
        # hull
        self.original_image = pygame.image.load(join('images', 'player', '0.png')).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-80, -70)
        
        # movement
        self.direction = pygame.Vector2()
        self.speed = 250
        self.rotation_speed = 180
        self.collision_sprites = collision_sprites
        self.move_forward = 0
        
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
        # if self.move_forward != 0:
        #     movement_vector = pygame.Vector2(0, -1).rotate(-self.rotation) * self.move_forward
        #     self.direction = movement_vector
        #     self.rect.x += movement_vector.x * self.speed * dt
        #     self.collisions('horizontal')
        #     self.rect.y += movement_vector.y * self.speed * dt
        #     self.collisions('vertical')
        
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
        # for sprite in self.collision_sprites:
        #     if sprite.rect.colliderect(self.rect):
            #     if direction == 'horizontal':
            #         if self.direction.x > 0: self.rect.right = sprite.rect.left
            #     if self.direction.x < 0: self.rect.left = sprite.rect.right
            # if direction == 'vertical':
            #     if self.direction.y > 0: self.rect.bottom = sprite.rect.top
            #     if self.direction.y < 0: self.rect.top = sprite.rect.bottom
                
        """Returns True if there is a collision with any sprite"""
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                return True
        return False
    
    def update(self, dt):
        self.input(dt)
        self.move(dt)