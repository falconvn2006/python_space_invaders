import pygame
import sys

# CONSTANTS
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 700

GREY = (29, 29, 27)
YELLOW = (243, 216, 63)

class Alien(pygame.sprite.Sprite):
    def __init__(self, type, x, y):
        super().__init__()
        self.type = type
        path = f"../images/alien_{self.type}.png"
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(topleft=(x,y))

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface((3, 3))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(topleft=(x,y))

class Obstacle:
    def __init__(self, x, y):
        self.grid = [
[0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
[0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
[0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1],
[1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1],
[1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1]]
        
        self.blocks_group = pygame.sprite.Group()
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):
                if self.grid[row][col] == 1:
                    pos_x = x + col * 3
                    pos_y = y + row * 3
                    block = Block(pos_x, pos_y)
                    self.blocks_group.add(block)

class Laser(pygame.sprite.Sprite):
    def __init__(self, position, speed):
        super().__init__()
        self.speed = speed

        self.image = pygame.Surface((4,15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=position)

    def update(self):
        self.rect.y -= self.speed

        # Remove the object if out of screen bound
        if self.rect.y > SCREEN_HEIGHT + 15 or self.rect.y < 0:
            # print("OUT OF BOUND")
            self.kill()

class SpaceShip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed = 6

        # Spaceship sprite setup
        self.image = pygame.image.load("../images/spaceship.png")
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH/2, SCREEN_HEIGHT))

        # Laser setup
        self.lasers_group = pygame.sprite.Group()
        self.laser_ready = True
        self.laser_time_after_shoot = 0 # milisecond
        self.laser_delay = 300 # milisecond

    def get_user_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.laser_ready:
            self.laser_ready = False
            laser = Laser(position=self.rect.center, speed=5)
            self.lasers_group.add(laser)
            self.laser_time_after_shoot =pygame.time.get_ticks()

    def update(self):
        self.get_user_input()
        self.constrain_movement()
        self.lasers_group.update()
        self.recharge_laser()

    def constrain_movement(self):
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        if self.rect.left < 0:
            self.rect.left = 0

    def recharge_laser(self):
        if not self.laser_ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time_after_shoot >= self.laser_delay:
                self.laser_ready = True


# Main game class
class SpaceInvaders:
    def __init__(self):
        # Game setup
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()

        # Space ship setup
        self.spaceship = SpaceShip()
        self.spaceship_group = pygame.sprite.GroupSingle()
        self.spaceship_group.add(self.spaceship)

        # Obstacles setup
        self.obstacles = self.create_obstacles()

        # Aliens setup
        self.aliens_group = pygame.sprite.Group()
        self.create_aliens()

    def create_obstacles(self):
        obstacle_width = len(Obstacle(0, 0).grid[0]) * 3
        gap = (SCREEN_WIDTH - (4 * obstacle_width)) / 5
        obstacles = []
        for i in range (4):
            offset_x = (i+1) * gap + i * obstacle_width
            obstacle = Obstacle(offset_x, SCREEN_HEIGHT - 100)
            obstacles.append(obstacle)

        return obstacles

    def create_aliens(self):
        # TODO: Change the row and col in range so that it can be customize able
        for row in range(5):
            for col in range(11):
                x = col * 55
                y = row * 55
                alien = Alien(1, x, y)
                self.aliens_group.add(alien)


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Update
            self.spaceship_group.update()

            # Render
            self.screen.fill(GREY)
            self.spaceship_group.draw(self.screen)
            self.spaceship_group.sprite.lasers_group.draw(self.screen)
            self.aliens_group.draw(self.screen)

            for obstacle in self.obstacles:
                obstacle.blocks_group.draw(self.screen)

            pygame.display.update()
            self.clock.tick(60)

game = SpaceInvaders()
game.run()