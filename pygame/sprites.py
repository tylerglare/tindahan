import pygame
from config import *
import math
import random

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert_alpha()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        self.last_move = pygame.time.get_ticks()
        self.move_delay = 20
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x, self.y = x * TILESIZE, y * TILESIZE
        self.width, self.height = TILESIZE, TILESIZE
        self.image = self.game.character_spritesheet.get_sprite(0, 0, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y

        # Movement
        self.x_change, self.y_change = 0, 0
        self.facing = "down"
        self.moving = False

        # Walking Animations
        self.down_animations = [self.game.mainwalkright_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.up_animations = [self.game.mainwalkright_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.left_animations = [self.game.mainwalkleft_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.right_animations = [self.game.mainwalkright_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]

        # Idle Animations
        self.idle_right_animations = [self.game.character_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.idle_left_animations = [self.game.character_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.idle_up_animations = [self.game.character_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.idle_down_animations = [self.game.character_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]

        self.animation_index = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 150

    def update(self):
        self.movement()
        self.animate()

        # Save old position
        old_x, old_y = self.rect.x, self.rect.y

        self.rect.x += self.x_change
        if self.collide_solid("x") or self.out_of_bounds():
            self.rect.x = old_x  # Prevents movement

        self.rect.y += self.y_change
        if self.collide_solid("y") or self.out_of_bounds():
            self.rect.y = old_y  # Prevents movement

        # Reset movement change
        self.x_change, self.y_change = 0, 0

    def movement(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        if now - self.last_move < self.move_delay:
            return

        self.last_move = now
        self.moving = False

        if keys[pygame.K_LEFT]:
            self.x_change = -PLAYER_SPEED
            self.facing = 'left'
            self.moving = True
        if keys[pygame.K_RIGHT]:
            self.x_change = PLAYER_SPEED
            self.facing = 'right'
            self.moving = True
        if keys[pygame.K_UP]:
            self.y_change = -PLAYER_SPEED
            self.facing = 'up'
            self.moving = True
        if keys[pygame.K_DOWN]:
            self.y_change = PLAYER_SPEED
            self.facing = 'down'
            self.moving = True

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.animation_index = (self.animation_index + 1) % 4

            if self.moving:
                if self.facing == "down":
                    self.image = self.down_animations[self.animation_index]
                elif self.facing == "up":
                    self.image = self.up_animations[self.animation_index]
                elif self.facing == "left":
                    self.image = self.left_animations[self.animation_index]
                elif self.facing == "right":
                    self.image = self.right_animations[self.animation_index]
            else:
                if self.facing == "down":
                    self.image = self.idle_down_animations[self.animation_index]
                elif self.facing == "up":
                    self.image = self.idle_up_animations[self.animation_index]
                elif self.facing == "left":
                    self.image = self.idle_left_animations[self.animation_index]
                elif self.facing == "right":
                    self.image = self.idle_right_animations[self.animation_index]

    def collide_solid(self, direction):
        """Prevents the player from walking through enemies or blocks."""
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.enemies, False) or pygame.sprite.spritecollide(self, self.game.blocks, False)
            return bool(hits)

        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.enemies, False) or pygame.sprite.spritecollide(self, self.game.blocks, False)
            return bool(hits)

    def out_of_bounds(self):
        """Prevents the player from going beyond the game borders."""
        return (
            self.rect.left < 0 or
            self.rect.right > WIN_WIDTH or
            self.rect.top < 0 or
            self.rect.bottom > WIN_HEIGHT
        )

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, name="Tambay"):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Movement
        self.movement_loop = 0
        self.max_travel = 5 * TILESIZE
        self.idle = False
        self.idle_time = 0
        self.speed = ENEMY_SPEED
        self.start_tile = (self.rect.x, self.rect.y)

        # Direction
        self.facing = random.choice(['down', 'left', 'right'])
        self.animation_loop = 0
        self.last_update = pygame.time.get_ticks()
        self.animations = {
            "up": self.load_animations(self.game.enemywalkright_spritesheet),
            "down": self.load_animations(self.game.enemywalkright_spritesheet),
            "left": self.load_animations(self.game.enemywalkleft_spritesheet),
            "right": self.load_animations(self.game.enemywalkright_spritesheet),
            "idle": self.load_animations(self.game.enemyidle_spritesheet)
        }

        self.image = self.animations[self.facing][0]
        self.image.set_colorkey(BLACK)

        self.name = name  # NPC name for dialogue
        self.removed = False  # New flag to check if NPC should be deleted
    
    def load_animations(self, spritesheet):
        return [
            spritesheet.get_sprite(i * TILESIZE, 0, self.width, self.height)
            for i in range(4)
        ]
    
    def update(self):
        if not self.removed:  # Only update if NPC is not removed
            self.movement()
            self.animate()
            self.detect_player()

    def movement(self):
        if self.idle:
            if pygame.time.get_ticks() - self.idle_time > 3000:
                self.idle = False
                self.facing = random.choice(['down', 'left', 'right'])
                self.rect.topleft = self.start_tile
        else:
            if self.facing == 'up':
                self.rect.y -= self.speed
            elif self.facing == 'down':
                self.rect.y += self.speed
            elif self.facing == 'left':
                self.rect.x -= self.speed
            elif self.facing == 'right':
                self.rect.x += self.speed
            
            self.movement_loop += self.speed
            if self.movement_loop >= self.max_travel:
                self.idle = True
                self.idle_time = pygame.time.get_ticks()
                self.movement_loop = 0
                self.start_tile = (self.rect.x, self.rect.y)

            self.rect.x = max(0, min(self.rect.x, WIN_WIDTH - self.width))
            self.rect.y = max(0, min(self.rect.y, WIN_HEIGHT - self.height))

    def animate(self):
        """Fixes animation logic."""
        if self.idle:
            animation_list = self.animations["idle"]
        else:
            animation_list = self.animations.get(self.facing, self.animations["idle"])

        if animation_list:
            self.image = animation_list[int(self.animation_loop) % len(animation_list)]
            self.animation_loop += 0.1

    def detect_player(self):
        """Detects player within 3 tiles and moves toward them."""
        if self.removed:  # If NPC is removed, do nothing
            return

        player_x, player_y = self.game.player.rect.x, self.game.player.rect.y
        distance_x = abs(self.rect.x - player_x)
        distance_y = abs(self.rect.y - player_y)

        if distance_x + distance_y <= 3 * TILESIZE:
            self.move_to_player(player_x, player_y)

    def move_to_player(self, player_x, player_y):
        """Moves NPC to the front of the player smoothly."""
        if self.removed:  # If NPC is removed, do nothing
            return

        target_x, target_y = self.get_position_in_front_of_player(player_x, player_y)

        dx = self.speed if self.rect.x < target_x else -self.speed
        dy = self.speed if self.rect.y < target_y else -self.speed

        if self.rect.x != target_x:
            self.facing = "right" if dx > 0 else "left"
            self.rect.x += dx

        if self.rect.y != target_y:
            self.facing = "down" if dy > 0 else "up"
            self.rect.y += dy

        self.animate()

        if self.rect.x == target_x and self.rect.y == target_y:
            self.game.show_convo(self)

    def get_position_in_front_of_player(self, player_x, player_y):
        """Finds the position directly in front of the player."""
        if self.game.player.facing == "up":
            return (player_x, player_y + TILESIZE)
        elif self.game.player.facing == "down":
            return (player_x, player_y - TILESIZE)
        elif self.game.player.facing == "left":
            return (player_x + TILESIZE, player_y)
        elif self.game.player.facing == "right":
            return (player_x - TILESIZE, player_y)
        return (player_x, player_y)  # Default to player's position

    def remove_npc(self):
        """Removes NPC permanently."""
        self.removed = True
        self.kill()  # Remove from sprite groups


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        
        self.image = self.game.terrain_spritesheet.get_sprite(960, 448, self.width, self.height)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(64, 352, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        self.font = pygame.font.Font('arial.ttf', fontsize)
        self.content = content
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg
        
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False
    
class Attack(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE

        self.animation_loop = 0

        self.image = self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.right_animations = [self.game.attack_spritesheet.get_sprite(0, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 64, self.width, self.height)]

        self.down_animations = [self.game.attack_spritesheet.get_sprite(0, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 32, self.width, self.height)]

        self.left_animations = [self.game.attack_spritesheet.get_sprite(0, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 96, self.width, self.height)]

        self.up_animations = [self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(32, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(64, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(96, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(128, 0, self.width, self.height)]
        

    def update(self):
        self.animate()
        self.collide()

    def collide(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, True)

    def animate(self):
        direction = self.game.player.facing

        if direction == 'up':
            self.image = self.up_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'down':
            self.image = self.down_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'left':
            self.image = self.left_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'right':
            self.image = self.right_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()
