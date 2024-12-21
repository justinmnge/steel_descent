from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import *

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Steel Descent')
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_images()
        
        # Load font
        self.font = pygame.font.Font(join('fonts', 'Tiny5-Regular.ttf'), 60)  # Adjust the size to your needs
        self.score_font = pygame.font.Font(join('fonts', 'Tiny5-Regular.ttf'), 60)  # Larger font for score
        
        # Initialize health and hit counter
        self.health = 100  # Starting health (100%)
        self.hit_counter = 0  # Number of hits
        self.score = 0  # Starting score
        self.score_timer = pygame.time.get_ticks()  # Timer to track score increments
        self.score_interval = 400  # Time in milliseconds for score increment (1 second)
        
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.shell_sprites = pygame.sprite.Group()
        self.impact_animations = pygame.sprite.Group()  # Create a group for impact animations
        
        # setup
        self.setup()
        
        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 600
        
        # Explosion animation setup (empty for now)
        self.explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')) for i in range(8)]
        self.explosion_index = 0
        self.explosion_active = False
        self.explosion_position = pygame.Vector2(0, 0)
    
    def display_text(self, text, position, color=(255, 255, 255), font=None):
        font = font or self.font
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        self.display_surface.blit(text_surface, text_rect)
    
    def update_health(self):
        # Update health based on hits
        if self.hit_counter == 1:
            self.health = 75
        elif self.hit_counter == 2:
            self.health = 50
        elif self.hit_counter == 3:
            self.health = 25
        elif self.hit_counter >= 4:
            self.health = 0  # Game Over
    
    # Set the color based on health
        if self.health == 0:
            self.health_color = (255, 0, 0)  # Red color for game over
        else:
            self.health_color = (255, 255, 255)  # Default white color
    
    def update_score(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.score_timer >= self.score_interval:
            self.score += 1  # Increase score by 10 points (adjust as needed)
            self.score_timer = current_time  # Reset the timer
    
    def load_images(self):
        self.shell_surf = pygame.image.load(join('images', 'fire', 'player_shell.png')).convert_alpha()
    
    def input(self):
        # mouse left-click
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            # Get mouse position relative to screen center
            mouse_pos = pygame.mouse.get_pos()
            screen_center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            
            # Calculate direction vector
            direction = pygame.Vector2(mouse_pos) - pygame.Vector2(screen_center)
            direction = direction.normalize()
            
            # Calculate spawn position relative to turret
            spawn_offset = direction * 66
            spawn_pos = pygame.Vector2(self.turret.rect.center) + spawn_offset
            
            # Adjustable X offset
            x_offset = 0
            
            # Create shell
            Shell(self.shell_surf, spawn_pos, direction, (self.all_sprites, self.shell_sprites), x_offset, self.collision_sprites)
            
            # Start firing animation
            self.turret.start_firing()
            
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
    
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
    
    def setup(self):
        # pytmx map
        map = load_pygame(join('data', 'maps', 'map.tmx'))
        
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            sprite = Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
            sprite.z = 0  # Add z attribute
            self.all_sprites.add(sprite)
            self.all_sprites.change_layer(sprite, sprite.z)
            
        for obj in map.get_layer_by_name('Objects'):
            sprite = CollisionSprite(
                (obj.x, obj.y), 
                obj.image, 
                (self.all_sprites, self.collision_sprites),
                hitbox_inflation=(-50, -50) # Adjust hitbox here
            ) 
            sprite.z = 1  # Add z attribute
            self.all_sprites.add(sprite)
            self.all_sprites.change_layer(sprite, sprite.z)
            
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
            
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.player.z = 2  # Add z attribute
                self.all_sprites.add(self.player)
                self.all_sprites.change_layer(self.player, self.player.z)
                
                self.turret = Turret(self.player, self.all_sprites)
                self.turret.z = 3  # Add z attribute
                self.all_sprites.add(self.turret)
                self.all_sprites.change_layer(self.turret, self.turret.z)
    
    def spawn_impact_animation(self, position, mouse_pos, direction):
        # Add the ImpactAnimation to the group
        impact_animation = ImpactAnimation(position, (self.all_sprites, self.impact_animations), mouse_pos, direction)
    
    def handle_explosion(self):
        if self.health == 0 and not self.explosion_active:
            # Set explosion position to player's location
            self.explosion_position = pygame.Vector2(self.player.rect.center)
            self.explosion_active = True
    
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000            
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            
            # Handle health, score and explosion
            self.update_health()
            self.update_score()
            self.handle_explosion()
            
            # draw
            self.display_surface.fill('black')
            self.all_sprites.custom_draw(self.player.rect.center)  # Changed from draw to custom_draw
            self.turret.draw(self.display_surface, self.player.rect.center)
            self.impact_animations.draw(self.display_surface)
            
            # Display Health Text
            self.display_text(f"Health: {self.health}%", (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100), self.health_color)
            
            # Game Over condition - Trigger explosion
            if self.health == 0:
                self.display_text("Game Over", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), (255, 0, 0))  # Red text

                # Explosion animation
                if self.explosion_active:
                    if self.explosion_index < len(self.explosion_frames):
                        explosion_frame = self.explosion_frames[self.explosion_index]
                        explosion_rect = explosion_frame.get_rect(center=self.explosion_position)
                        self.display_surface.blit(explosion_frame, explosion_rect)
                        self.explosion_index += 1
                    else:
                        # Reset after explosion finishes
                        self.explosion_active = False
                        self.explosion_index = 0
            
            # Display Score Text (bottom center)
            self.display_text(f"SCORE: {self.score}", (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50), font=self.score_font)
                                      
            pygame.display.update()
        
    pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()