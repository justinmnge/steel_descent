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
        
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.shell_sprites = pygame.sprite.Group()
        
        # setup
        self.setup()
        
        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 600
    
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
            Shell(self.shell_surf, spawn_pos, direction, (self.all_sprites, self.shell_sprites), x_offset)
            
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
            sprite = CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
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
            
            # draw
            self.display_surface.fill('black')
            self.all_sprites.custom_draw(self.player.rect.center)  # Changed from draw to custom_draw
            self.turret.draw(self.display_surface, self.player.rect.center)
            
            pygame.display.update()
        
    pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()