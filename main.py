import pygame
import sys, random

# CONSTANTS / GAME SETTINGS
# TODO: Add some of these constant to the main code
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 700
OFFSET = 50
PLAYER_SPEED = 6
PLAYER_FIRE_RATE = 300
PLAYER_LIVES = 3

LOAD_OLD_HIGH_SCORE = True
SAVE_HIGH_SCORE_TO_FILE = True

MUSIC_VERSION = 2

# COLOR CONST
GREY = (29, 29, 27)
YELLOW = (243, 216, 63)
RED = (255, 0, 0)

class Alien(pygame.sprite.Sprite):
    def __init__(self, type, x, y):
        super().__init__()
        self.type = type
        path = f"images/alien_{self.type}.png"
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(topleft=(x,y))

    def update(self, direction):
        self.rect.x += direction

class MysteryShips(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/mystery.png")

        # Random starting x
        x = random.choice([OFFSET/2, SCREEN_WIDTH + OFFSET - self.image.get_width()])
        if x == OFFSET/2:
            self.speed = 3
        else:
            self.speed = -3

        self.rect = self.image.get_rect(topleft = (x, 90))

    def update(self):
        self.rect.x += self.speed

        if self.rect.right > SCREEN_WIDTH + OFFSET/2:
            self.kill()
        elif self.rect.left < OFFSET/2:
            self.kill()

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
        self.image = pygame.image.load("images/spaceship.png")
        self.rect = self.image.get_rect(midbottom=((SCREEN_WIDTH + OFFSET)/2, SCREEN_HEIGHT))

        # Laser setup
        self.lasers_group = pygame.sprite.Group()
        self.laser_ready = True
        self.laser_time_after_shoot = 0 # milisecond
        self.laser_delay = 300 # milisecond
        self.laser_sound = pygame.mixer.Sound("sounds/laser.ogg")

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
            self.laser_sound.play()

    def update(self):
        self.get_user_input()
        self.constrain_movement()
        self.lasers_group.update()
        self.recharge_laser()

    def constrain_movement(self):
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        if self.rect.left < OFFSET:
            self.rect.left = OFFSET

    def recharge_laser(self):
        if not self.laser_ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time_after_shoot >= self.laser_delay:
                self.laser_ready = True

    def reset(self):
        self.rect = self.image.get_rect(midbottom=((SCREEN_WIDTH+OFFSET)/2, SCREEN_HEIGHT))
        self.lasers_group.empty()


# Main game class
class SpaceInvaders:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + OFFSET, SCREEN_HEIGHT + OFFSET*2))
        pygame.display.set_caption("Space Invaders")

        # Font setup
        self.font = pygame.font.Font("font/monogram.ttf", 40)
        self.level_surface = self.font.render("LEVEL 00", False, YELLOW)
        self.game_over_surface = self.font.render("GAME OVER", False, RED)
        self.reset_surface = self.font.render("SPACE TO RESTART", False, RED)
        self.score_text_surface = self.font.render("SCORE", False, YELLOW)
        self.high_score_text_surface = self.font.render("HIGH-SCORE", False, YELLOW)

        # Game setup
        self.clock = pygame.time.Clock()
        self.lives = PLAYER_LIVES
        self.player_is_alive = True
        self.score = 0
        self.high_score = 0
        self.load_high_score()

        # Sound/Music setup
        pygame.mixer.music.load(f"sounds/music_v{MUSIC_VERSION}.ogg")
        pygame.mixer.music.play(-1)
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.ogg")

        # CUSTOM EVENTS
        self.SHOOT_LASER = pygame.USEREVENT
        pygame.time.set_timer(self.SHOOT_LASER, 500)
        self.MYSTERY_SHIP = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MYSTERY_SHIP, random.randint(4000, 8000))

        # Space ship setup
        self.spaceship = SpaceShip()
        self.spaceship_group = pygame.sprite.GroupSingle()
        self.spaceship_group.add(self.spaceship)

        # Obstacles setup
        self.obstacles = self.create_obstacles()

        # Aliens setup
        self.aliens_direction = 1
        self.aliens_group = pygame.sprite.Group()
        self.create_aliens()

        self.alien_lasers_group = pygame.sprite.Group()

        # Mystery ship
        self.mystery_ship_group = pygame.sprite.GroupSingle()

    def create_obstacles(self):
        obstacle_width = len(Obstacle(0, 0).grid[0]) * 3
        gap = (SCREEN_WIDTH + OFFSET - (4 * obstacle_width)) / 5
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
                x = 75 + col * 55
                y = 110 + row * 55

                if row == 0:
                    alien_type = 3
                elif row in range(1,2):
                    alien_type = 2
                else:
                    alien_type = 1

                alien = Alien(alien_type, x + OFFSET/2, y)
                self.aliens_group.add(alien)

    def move_aliens(self):
        self.aliens_group.update(self.aliens_direction)

        aliens_sprite = self.aliens_group.sprites()
        for alien in aliens_sprite:
            if alien.rect.right >= SCREEN_WIDTH + OFFSET/2:
                self.aliens_direction = -1
                self.move_aliens_down(2)
            elif alien.rect.left <= OFFSET/2:
                self.aliens_direction = 1
                self.move_aliens_down(2)

    def move_aliens_down(self, distance):
        if self.aliens_group:
            for alien in self.aliens_group.sprites():
                alien.rect.y += distance

    def alien_shoot_laser(self):
        if self.aliens_group.sprites():
            random_alien = random.choice(self.aliens_group.sprites())
            laser_sprite = Laser(random_alien.rect.center, -6)
            self.alien_lasers_group.add(laser_sprite)

    def create_mystery_ship(self):
        self.mystery_ship_group.add(MysteryShips())

    def check_for_collision(self):
        # Spaceship lasers collide with aliens
        if self.spaceship_group.sprite.lasers_group:
            for laser_sprite in self.spaceship_group.sprite.lasers_group:
                aliens_hit = pygame.sprite.spritecollide(laser_sprite, self.aliens_group, True)
                if aliens_hit:
                    self.explosion_sound.play()
                    for alien in aliens_hit:
                        self.score += alien.type * 100
                        self.check_for_high_score()
                        laser_sprite.kill()

                if pygame.sprite.spritecollide(laser_sprite, self.mystery_ship_group, True):
                    self.score += 500
                    self.check_for_high_score()
                    self.explosion_sound.play()
                    laser_sprite.kill()

                # Remove one block of obstacle in 4 if the player's laser hit it
                for obstacle in self.obstacles:
                    if pygame.sprite.spritecollide(laser_sprite, obstacle.blocks_group, True):
                        laser_sprite.kill()

        # Alien lasers collide with player
        if self.alien_lasers_group:
            for laser_sprite in self.alien_lasers_group:
                if pygame.sprite.spritecollide(laser_sprite, self.spaceship_group, False):
                    laser_sprite.kill()
                    self.lives -= 1

                    if self.lives <= 0:
                        self.game_over()
                    self.explosion_sound.play()
                
                for obstacle in self.obstacles:
                    if pygame.sprite.spritecollide(laser_sprite, obstacle.blocks_group, True):
                        laser_sprite.kill()
        
        if self.aliens_group:
            for alien in self.aliens_group:
                for obstacle in self.obstacles:
                    pygame.sprite.spritecollide(alien, obstacle.blocks_group, True)
                
                if pygame.sprite.spritecollide(alien, self.spaceship_group, False):
                    self.game_over()

    def game_over(self):
        self.player_is_alive = False
        print("Game Over")
    
    def reset(self):
        self.player_is_alive = True
        self.score = 0
        self.lives = PLAYER_LIVES
        self.spaceship_group.sprite.reset()

        self.aliens_group.empty()
        self.alien_lasers_group.empty()
        self.mystery_ship_group.empty()

        self.create_aliens()
        self.obstacles = self.create_obstacles()

    def check_for_high_score(self):
        # TODO: Save the high score to a file then load it when start game (DONE)
        self.high_score = max(self.score, self.high_score)

        if SAVE_HIGH_SCORE_TO_FILE:
            with open("highscore.txt", "w") as file:
                file.write(str(self.high_score))

    def load_high_score(self):
        if LOAD_OLD_HIGH_SCORE:
            try:
                with open("highscore.txt", "r") as file:
                    self.high_score = int(file.read())
            except FileNotFoundError:
                self.high_score = 0
                print("highscore.txt not found")

    def run(self):
        while True:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()

                if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                    pygame.quit()
                    sys.exit()

                if event.type == self.SHOOT_LASER and self.player_is_alive:
                    self.alien_shoot_laser()

                if event.type == self.MYSTERY_SHIP and self.player_is_alive:
                    self.create_mystery_ship()

                if keys[pygame.K_SPACE] and not self.player_is_alive:
                    self.reset()

            # Update
            if self.player_is_alive:
                self.spaceship_group.update()
                self.move_aliens()
                self.alien_lasers_group.update()
                self.mystery_ship_group.update()
                self.check_for_collision()

            # Render background
            self.screen.fill(GREY)

            # Draw UI
            pygame.draw.rect(self.screen, YELLOW, (10, 10, 780, 780), 2, 0, 60, 60, 60, 60)
            pygame.draw.line(self.screen, YELLOW, (25, 730), (775, 730), 3)
            if self.player_is_alive:
                self.screen.blit(self.level_surface, (570, 740, 50, 50))
            else:
                self.screen.blit(self.game_over_surface, (570, 740, 50, 50))
                self.screen.blit(self.reset_surface, (50, 740))

            x = 50
            for live in range(self.lives):
                self.screen.blit(self.spaceship_group.sprite.image, (x, 745))
                x += 50

            ## Score UI
            formatted_score = str(self.score).zfill(5)
            formatted_high_score = str(self.high_score).zfill(5)
            score_number_surface = self.font.render(formatted_score, False, YELLOW)
            high_score_number_surface = self.font.render(formatted_high_score, False, YELLOW)
            self.screen.blit(self.score_text_surface, (50, 15, 50, 50))
            self.screen.blit(score_number_surface, (50, 40, 50, 50))
            self.screen.blit(self.high_score_text_surface, (550, 15, 50, 50))
            self.screen.blit(high_score_number_surface, (550, 40, 50, 50))

            # Render the game objects
            if self.player_is_alive:
                self.spaceship_group.draw(self.screen)
            self.spaceship_group.sprite.lasers_group.draw(self.screen)
            self.aliens_group.draw(self.screen)
            self.alien_lasers_group.draw(self.screen)
            self.mystery_ship_group.draw(self.screen)

            for obstacle in self.obstacles:
                obstacle.blocks_group.draw(self.screen)

            pygame.display.update()
            self.clock.tick(60)

game = SpaceInvaders()
game.run()
