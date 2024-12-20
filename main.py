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
        
        pygame.mouse.set_visible(False)
        
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        
        # setup
        self.setup()
    
    def setup(self):
    # pytmx map
        map = load_pygame(join('data', 'maps', 'map.tmx'))
        
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            sprite = Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
            self.all_sprites.add(sprite)  # Add the sprite
            self.all_sprites.change_layer(sprite, 0)  # Set layer 0
            
        for obj in map.get_layer_by_name('Objects'):
            sprite = CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
            self.all_sprites.add(sprite)  # Add the sprite
            self.all_sprites.change_layer(sprite, 1)  # Set layer 1
            
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
            
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.all_sprites.add(self.player)  # Add the player sprite
                self.all_sprites.change_layer(self.player, 2)  # Set layer 2
                
                self.turret = Turret(self.player, self.all_sprites)
                self.all_sprites.add(self.turret)  # Add the turret sprite
                self.all_sprites.change_layer(self.turret, 3)  # Set layer 3
        
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000            
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # update
            self.all_sprites.update(dt)
            
            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)            
            pygame.display.update()
            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()