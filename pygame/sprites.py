import pygame
from config import *
import math
import random
import json

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

        # Coins
        self.coins = 20

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
            hits = pygame.sprite.spritecollide(self, self.game.npcs, False) or pygame.sprite.spritecollide(self, self.game.blocks, False)
            return bool(hits)

        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.npcs, False) or pygame.sprite.spritecollide(self, self.game.blocks, False)
            return bool(hits)

    def out_of_bounds(self):
      
        return (
            self.rect.left < 0 or
            self.rect.right > self.game.camera.width or
            self.rect.top < 0 or
            self.rect.bottom > self.game.camera.height
        )


class NPC(pygame.sprite.Sprite):
    NPC_SPRITESHEETS = {
        "Tambay": {
            "walk_right": 'img/TINDAHAN CHARACTERS/TAMBAY1 WALK RIGHT.png',
            "walk_left": 'img/TINDAHAN CHARACTERS/TAMBAY1 WALK LEFT.png',
            "idle": 'img/TINDAHAN CHARACTERS/TAMBAY1 IDLE RIGHT.png'
        },
        "Bata": {
            "walk_right": 'img/TINDAHAN CHARACTERS/BATA1 WALK RIGHT.png',
            "walk_left": 'img/TINDAHAN CHARACTERS/BATA1 WALK LEFT.png',
            "idle": 'img/TINDAHAN CHARACTERS/BATA1 IDLE RIGHT.png'
        }
        # Add more NPC types here
    }

    def __init__(self, game, x, y, name="Tambay", difficulty="easy"):
        self.game = game
        self.name = name
        self.difficulty = difficulty  # Add difficulty level
        self._layer = NPC_LAYER
        self.groups = self.game.all_sprites, self.game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Load the appropriate spritesheet based on the NPC type
        spritesheet = self.NPC_SPRITESHEETS[name]
        self.walk_right_spritesheet = Spritesheet(spritesheet["walk_right"])
        self.walk_left_spritesheet = Spritesheet(spritesheet["walk_left"])
        self.idle_spritesheet = Spritesheet(spritesheet["idle"])

        # Movement
        self.movement_loop = 0
        self.max_travel = 5 * TILESIZE
        self.idle = False
        self.idle_time = 0
        self.speed = NPC_SPEED
        self.start_tile = (self.rect.x, self.rect.y)
        self.start_x = x * TILESIZE
        self.start_y = y * TILESIZE
        self.direction = random.choice(['left', 'right'])  # Randomize initial direction

        # Direction
        self.facing = self.direction
        self.animation_loop = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 150  # Match player animation speed
        self.animations = {
            "up": self.load_animations(self.walk_right_spritesheet),
            "down": self.load_animations(self.walk_right_spritesheet),
            "left": self.load_animations(self.walk_left_spritesheet),
            "right": self.load_animations(self.walk_right_spritesheet),
            "idle": self.load_animations(self.idle_spritesheet)
        }

        self.image = self.animations[self.facing][0]

        self.name = name  # NPC name for dialogue
        self.removed = False  # New flag to check if NPC should be deleted
        self.asked_question = False  # Flag to ensure the question is asked only once
        
        with open('c:\\Users\\This PC\\OneDrive\\Documents\\054\\TindahanGame\\questions.json') as f:
            self.questions = json.load(f)

    def load_animations(self, spritesheet):
        animations = [
            spritesheet.get_sprite(i * TILESIZE, 0, self.width, self.height)
            for i in range(4)
        ]
        return animations
    
    def update(self):
        if not self.removed:  # Only update if NPC is not removed
            self.movement()
            self.animate()
            self.detect_player()

    def movement(self):
        if self.idle:
            if pygame.time.get_ticks() - self.idle_time > 3000:
                self.idle = False
                self.direction = random.choice(['left', 'right', 'up', 'down'])  # Randomize direction after idle
                self.rect.topleft = self.start_tile
        else:
            old_x, old_y = self.rect.x, self.rect.y

            if self.direction == 'right':
                self.rect.x += self.speed
                if self.rect.x >= self.start_x + self.max_travel or self.collide_with_blocks('x'):
                    self.rect.x = old_x
                    self.direction = random.choice(['left', 'up', 'down'])
            elif self.direction == 'left':
                self.rect.x -= self.speed
                if self.rect.x <= self.start_x - self.max_travel or self.collide_with_blocks('x'):
                    self.rect.x = old_x
                    self.direction = random.choice(['right', 'up', 'down'])
            elif self.direction == 'up':
                self.rect.y -= self.speed
                if self.rect.y <= self.start_y - self.max_travel or self.collide_with_blocks('y'):
                    self.rect.y = old_y
                    self.direction = random.choice(['down', 'left', 'right'])
            elif self.direction == 'down':
                self.rect.y += self.speed
                if self.rect.y >= self.start_y + self.max_travel or self.collide_with_blocks('y'):
                    self.rect.y = old_y
                    self.direction = random.choice(['up', 'left', 'right'])

            self.movement_loop += self.speed
            if self.movement_loop >= self.max_travel:
                self.idle = True
                self.idle_time = pygame.time.get_ticks()
                self.movement_loop = 0
                self.start_tile = (self.rect.x, self.rect.y)

            self.rect.x = max(0, min(self.rect.x, WIN_WIDTH - self.width))
            self.rect.y = max(0, min(self.rect.y, WIN_HEIGHT - self.height))

    def collide_with_blocks(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                return True
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                return True
        return False

    def animate(self):
        """Fixes animation logic."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            if self.idle:
                animation_list = self.animations["idle"]
            else:
                animation_list = self.animations.get(self.direction, self.animations["idle"])

            if animation_list:
                self.image = animation_list[int(self.animation_loop) % len(animation_list)]
                self.animation_loop += 1
                if self.animation_loop >= len(animation_list):
                    self.animation_loop = 0

    def detect_player(self):
        """Detects player within 3 tiles and moves toward them."""
        if self.removed or self.asked_question:  # If NPC is removed or already asked a question, do nothing
            return

        player_x, player_y = self.game.player.rect.x, self.game.player.rect.y
        distance_x = abs(self.rect.x - player_x)
        distance_y = abs(self.rect.y - player_y)

        if distance_x + distance_y <= 3 * TILESIZE:
            self.move_to_player(player_x, player_y)

    def move_to_player(self, player_x, player_y):
        if self.removed or self.asked_question:
            return

        target_x, target_y = self.get_position_in_front_of_player(player_x, player_y)

        distance_x = target_x - self.rect.x
        distance_y = target_y - self.rect.y

        if abs(distance_x) > 0:
            step_x = min(self.speed, abs(distance_x)) * (1 if distance_x > 0 else -1)
            self.rect.x += step_x
            self.facing = "right" if step_x > 0 else "left"

        if abs(distance_y) > 0:
            step_y = min(self.speed, abs(distance_y)) * (1 if distance_y > 0 else -1)
            self.rect.y += step_y
            self.facing = "down" if step_y > 0 else "up"

        if abs(distance_x) < self.speed and abs(distance_y) < self.speed:
            self.rect.x = target_x
            self.rect.y = target_y

            # Get a random question based on difficulty
            if self.difficulty == "easy":
                question_data = random.choice(self.questions['easy'])
            elif self.difficulty == "average":
                question_data = random.choice(self.questions['average'])
            elif self.difficulty == "hard":
                question_data = random.choice(self.questions['hard'])

            conversation = question_data.get('conversation', "Hello! I have a question for you.")
            question = question_data['question']
            choices = question_data['choices']
            correct_answer = question_data['correct_answer']
            self.game.show_question(conversation, question, self, choices, correct_answer)  # Pass all 5 arguments
            self.asked_question = True  # Set the flag to indicate the question has been asked

        self.animate()

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

    def out_of_bounds(self):
        """Prevents the player from going beyond the game borders."""
        return (
            self.rect.left < 0 or
            self.rect.right > WIN_WIDTH or
            self.rect.top < 0 or
            self.rect.bottom > WIN_HEIGHT
        )

    def return_to_spawn(self):
        """Returns the enemy to the spawn point and sets it to idle."""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.idle = True
        self.idle_time = pygame.time.get_ticks()
        self.asked_question = True  # Set the flag to indicate the enemy has asked a question

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y, obj_type):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set position based on tile size
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        # Load the full house image
        obj_images = {
            "H": "img/TINDAHAN CHARACTERS/BAHAY.png",
            "G": "img/TINDAHAN CHARACTERS/BAHAY2.png"
           
        }
        
        self.image = pygame.image.load(obj_images[obj_type]).convert_alpha()

        # Set correct width & height from image
        self.width, self.height = self.image.get_size()

        # Adjust rect size and position
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        
        
        self.image = pygame.image.load(obj_images[obj_type]).convert_alpha()

        # Set correct width & height from image
        self.width, self.height = self.image.get_size()

        # Adjust rect size and position
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

class Block2(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK2_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set position based on tile size
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        # Load the full house image
        self.image = pygame.image.load("img/TINDAHAN CHARACTERS/tree.png").convert_alpha()

        # Set correct width & height from image
        self.width, self.height = self.image.get_size()

        # Adjust rect size and position
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

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

class Road(pygame.sprite.Sprite):
    def __init__(self, game, x, y, road_type):
        self.game = game
        self._layer = ROAD_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set position based on tile size
        self.x = x * TILESIZE
        self.y = y * TILESIZE

        # Load specific road image based on road_type
        road_images = {
            1: "img/TINDAHAN CHARACTERS/road1.png",
            2: "img/TINDAHAN CHARACTERS/road2.png",
            3: "img/TINDAHAN CHARACTERS/road3.png",
            4: "img/TINDAHAN CHARACTERS/road4.png",
            5: "img/TINDAHAN CHARACTERS/road5.png",
            6: "img/TINDAHAN CHARACTERS/road6.png"
        }
        
        self.image = pygame.image.load(road_images[road_type]).convert_alpha()

        # Set correct width & height from image
        self.width, self.height = self.image.get_size()

        # Adjust rect size and position
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)


class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize, alpha=255):
        self.font = pygame.font.Font('PressStart2P-Regular.ttf', fontsize)
        self.content = content
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg
        self.alpha = alpha
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Correctly handle the color and alpha values
        self.image.fill((*self.bg, self.alpha))
        
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
        hits = pygame.sprite.spritecollide(self, self.game.npcs, True)

    def animate(self):
        direction = self.game.player.facing

        if direction == 'up':
            self.image = self.up_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.05
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'down':
            self.image = self.down_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.05
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

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """Moves entities based on the camera's offset."""
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        """Centers the camera on the player but keeps within the map bounds."""
        x = -target.rect.x + CAM_WIDTH // 2
        y = -target.rect.y + CAM_HEIGHT // 2

        # Keep the camera within map boundaries
        x = min(0, x)  # Left boundary
        x = max(-(self.width - CAM_WIDTH), x)  # Right boundary
        y = min(0, y)  # Top boundary
        y = max(-(self.height - CAM_HEIGHT), y)  # Bottom boundary

        self.camera = pygame.Rect(x, y, self.width, self.height)

