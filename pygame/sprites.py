import pygame
from config import *
import math
import random
import json
import os
from ui import DialogueBox


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
        self.image = self.game.mainidleright_spritesheet.get_sprite(0, 0, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        self.start_x = self.x  # Store the spawn point
        self.start_y = self.y  # Store the spawn point
        # Movement
        self.x_change, self.y_change = 0, 0
        self.facing = "down"
        self.moving = False

        # Coins
        self.coins = 0
        self.inventory = []

        # Walking Animations
        self.down_animations = [self.game.mainwalkright_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.down_animations = [self.game.mainwalkleft_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.up_animations = [self.game.mainwalkright_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.up_animations = [self.game.mainwalkleft_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.left_animations = [self.game.mainwalkleft_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.right_animations = [self.game.mainwalkright_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]

        # Idle Animations
        self.idle_right_animations = [self.game.mainidleright_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        self.idle_left_animations = [self.game.mainidleleft_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        #self.idle_up_animations = [self.game.character_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]
        #self.idle_down_animations = [self.game.character_spritesheet.get_sprite(i * TILESIZE, 0, TILESIZE, TILESIZE) for i in range(4)]

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

        horizontal_movement = False

        # Horizontal movement takes priority for facing direction
        if keys[pygame.K_a]:
            self.x_change = -PLAYER_SPEED
            self.facing = 'left'
            self.moving = True
            horizontal_movement = True
        if keys[pygame.K_d]:
            self.x_change = PLAYER_SPEED
            self.facing = 'right'
            self.moving = True
            horizontal_movement = True
        
        # Vertical movement doesn't override facing direction if a horizontal direction was last pressed
        if keys[pygame.K_w]:
            self.y_change = -PLAYER_SPEED
            self.moving = True
        elif keys[pygame.K_s]:
            self.y_change = PLAYER_SPEED
            self.moving = True


    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.animation_index = (self.animation_index + 1) % 4

            if self.moving:
                if self.facing == "left":
                    self.image = self.left_animations[self.animation_index]
                elif self.facing == "right":
                    self.image = self.right_animations[self.animation_index]
                elif self.facing == "up":
                    self.image = self.up_animations[self.animation_index]
                elif self.facing == "down":
                    self.image = self.down_animations[self.animation_index]
            else:
                # Force idle to last left or right direction
                if self.facing == "left":
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
    
    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
    
    def has_item(self, item):
        return item in self.inventory

class NPC(pygame.sprite.Sprite):
    NPC_SPRITESHEETS = {
        "Tambay": {
            "walk_right": 'img/TINDAHAN CHARACTERS/TAMBAY1 WALK RIGHT.png',
            "walk_left": 'img/TINDAHAN CHARACTERS/TAMBAY1 WALK LEFT.png',
            "idle": 'img/TINDAHAN CHARACTERS/TAMBAY1 IDLE RIGHT.png',
            "portrait": 'img/PROFILE/TAMBAYP.png',
            "name": "Tambay"
        },
        "Bata": {
            "walk_right": 'img/TINDAHAN CHARACTERS/BATA1 WALK RIGHT.png',
            "walk_left": 'img/TINDAHAN CHARACTERS/BATA1 WALK LEFT.png',
            "idle": 'img/TINDAHAN CHARACTERS/BATA1 IDLE RIGHT.png',
            "portrait": 'img/PROFILE/BATAP.png',
            "name": "Bata"
        },
        "Teacher": {
            "walk_right": 'img/TINDAHAN CHARACTERS/TEACHER WALK RIGHT.png',
            "walk_left": 'img/TINDAHAN CHARACTERS/TEACHER WALK LEFT.png',
            "idle": 'img/TINDAHAN CHARACTERS/TEACHER IDLE RIGHT.png',
            "portrait": 'img/PROFILE/TEACHERP.png',
            "name": "Teacher"
        },
        "AlingNena": {
            "idle": 'img/TINDAHAN CHARACTERS/ALINGNENA IDLE RIGHT.png',
            "portrait": 'img/PROFILE/NENAP.png',
            "name": "Nena"
        },
        "Nanay": {
            "idle": 'img/TINDAHAN CHARACTERS/NANAY IDLE RIGHT.png',
            "portrait": 'img/PROFILE/NANAYP.png',
            "name": "Nanay"
        }
        # Add more NPC types here
    }

    def __init__(self, game, x, y, name="Tambay", difficulty="easy"):
        self.game = game
        self.name = name
        self.sprites = NPC.NPC_SPRITESHEETS.get(name)
        self.portrait_path = self.sprites.get('portrait')
        self.difficulty = difficulty  # Default difficulty, will be updated dynamically
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

            # Determine difficulty based on loop count
            difficulty = "easy" if self.game.loop_count == 0 else "average" if self.game.loop_count == 1 else "hard"

            # Select a random question from the current difficulty
            question_data = random.choice(self.questions[difficulty])
            conversation = question_data['conversation']
            question = question_data['question']
            choices = question_data['choices']
            correct_answer = question_data['correct_answer']
            responses = question_data.get('responses')

            # Show the question
            self.game.show_question(
                conversation,
                question,
                self,
                choices,
                correct_answer,
                responses,
                difficulty  # Pass the difficulty argument
            )
            self.asked_question = True

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
        self.asked_question = False  # Reset the flag to allow new questions


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
            "G": "img/TINDAHAN CHARACTERS/BAHAY2.png",
            "Y": "img/TINDAHAN CHARACTERS/BAHAY3.png",
            "L": "img/TINDAHAN CHARACTERS/BAHAY4.png"
           
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

class School(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK2_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set position based on tile size
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        # Load the full house image
        self.image = pygame.image.load("img/TINDAHAN CHARACTERS/SCHOOL.png").convert_alpha()

        # Set correct width & height from image
        self.width, self.height = self.image.get_size()

        # Adjust rect size and position
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

class Zone(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK2_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set position based on tile size
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        # Load the full house image
        self.image = pygame.image.load("img/TINDAHAN CHARACTERS/sign.png").convert_alpha()

        # Set correct width & height from image
        self.width, self.height = self.image.get_size()

        # Adjust rect size and position
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

class Shop(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK2_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set position based on tile size
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        # Load the full house image
        self.image = pygame.image.load("img/TINDAHAN CHARACTERS/NENAS.png").convert_alpha()

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
    def __init__(self, x, y, width, height, bg, fg, content, fontsize, alpha=255):
        self.font = pygame.font.Font(('PressStart2P-Regular.ttf'), fontsize)  # Use the passed fontsize
        self.content = content
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bg = bg
        self.fg = fg
        self.alpha = alpha

        if isinstance(bg, str) and os.path.exists(bg):
            # Load the image as the background
            self.image = pygame.image.load(bg).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else:
            # Use a color as the background
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.image.fill((*bg, self.alpha))
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Initial render of the text
        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width / 2, self.height / 2))
        self.image.blit(self.text, self.text_rect)
        
    def draw(self, screen):
        # Draw the button onto the screen
        screen.blit(self.image, self.rect)

    def update_text(self, new_content):
        """Update the text on the button and refresh the background."""
        self.content = new_content
        # Render the new text
        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width / 2, self.height / 2))

        # Clear the previous text (if any) and redraw the background
        if isinstance(self.bg, tuple):  # If it's a solid color background
            self.image.fill((*self.bg, self.alpha))
        else:  # If it's an image background, reload and rescale it
            self.image = pygame.image.load(self.bg).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))

        # Draw the new text over the background
        self.image.blit(self.text, self.text_rect)
        
    def is_pressed(self, pos, pressed):
        """Check if the button is pressed."""
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False
    

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

class AlingNena(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = NPC_LAYER
        self.groups = self.game.all_sprites, self.game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Load spritesheets
        self.left_spritesheet = self.game.alingnenaleft_spritesheet
        self.right_spritesheet = self.game.alingnenaright_spritesheet

        # Movement
        self.movement_loop = 0
        self.idle = False
        self.idle_time = 0
        self.speed = NPC_SPEED
        self.start_tile = (self.rect.x, self.rect.y)
        self.start_x = x * TILESIZE
        self.start_y = y * TILESIZE
        self.start_x = self.rect.x  # Save starting position
        self.start_y = self.rect.y
        self.direction = 'right'  # Start facing right

        # Direction
        self.facing = self.direction
        self.animation_loop = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 200  # Slower animation
        
        # Load animations
        self.animations = {
            "left": self.load_animations(self.left_spritesheet),
            "right": self.load_animations(self.right_spritesheet),
            "idle": self.load_animations(self.right_spritesheet)  # Use right as idle
        }

        self.image = self.animations[self.facing][0]
        self.name = "Aling Nena"
        self.asked_question = False  # Initialize interaction flag
        self.removed = False
        
        npc_data = NPC.NPC_SPRITESHEETS["AlingNena"]
        self.name = npc_data["name"]
        self.portrait_path = npc_data["portrait"]

        # Special dialogue for Aling Nena
        self.dialogue = [
            "Welcome to my store!",
            "What can I get for you today?",
            "We have fresh items just arrived!"
        ]

        self.item_prices = {
            "Milk": 10,
            "Bread": 5,
            "Toyo": 8,
            "Suka": 8,
            "Rice": 8,
            "Eggs": 15
        }

    def load_animations(self, spritesheet):
        animations = [
            spritesheet.get_sprite(i * TILESIZE, 0, self.width, self.height)
            for i in range(4)
        ]
        return animations

    def animate(self):
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
        if self.removed or self.asked_question:
            return

        player_x, player_y = self.game.player.rect.center
        npc_x, npc_y = self.rect.center

        distance = math.sqrt((npc_x - player_x) ** 2 + (npc_y - player_y) ** 2)

        if distance <= 2 * TILESIZE:
            self.game.handle_alingnena_interaction()
            self.asked_question = True
            self.asked_question = not self.asked_question


    def update(self):
        if not self.removed:
            self.animate()
            self.detect_player()
        else:
            # ✅ Reset interaction state after game reset
            self.asked_question = False

    def buy_item(self, item):
        if item in self.item_prices:
            price = self.item_prices[item]
            if self.game.player.coins >= price:
                self.game.player.coins -= price
                self.game.show_task_dialogue(
                    f"You bought {item} for {price} coins!",
                    self,
                    [],  # ✅ Fix here!
                    None,
                    "You successfully completed the task!",
                    "You failed to complete the task!"
                )
                nanay = next((npc for npc in self.game.npcs if isinstance(npc, Nanay)), None)
                if nanay:
                    nanay.complete_task(self.game.player)
                    nanay.check_task_completion(item)
                self.game.task_success = True
                self.asked_question = False
                self.game.reset_game()
            else:
                self.game.show_task_dialogue(
                    "You don't have enough coins!",
                    self,
                    [],  # ✅ Fix here!
                    None,
                    None,
                    None
                )
                
                self.game.reset_game()
                self.asked_question = False 



class Nanay(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = NPC_LAYER
        self.groups = self.game.all_sprites, self.game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Use the NPC_SPRITESHEETS dictionary to get the name and portrait
        npc_data = NPC.NPC_SPRITESHEETS["Nanay"]
        self.name = npc_data["name"]
        self.portrait_path = npc_data["portrait"]

        # Load spritesheets
        self.left_spritesheet = self.game.nanayleft_spritesheet
        self.right_spritesheet = self.game.nanayright_spritesheet

        # Movement
        self.movement_loop = 0
        self.max_travel = 4 * TILESIZE
        self.idle = False
        self.idle_time = 0
        self.speed = NPC_SPEED * 0.75  # Slower movement
        self.start_tile = (self.rect.x, self.rect.y)
        self.start_x = x * TILESIZE
        self.start_y = y * TILESIZE
        self.direction = 'left'

        # Direction
        self.facing = self.direction
        self.animation_loop = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 250  # Slower animation
        
        # Load animations
        self.animations = {
            "left": self.load_animations(self.left_spritesheet),
            "right": self.load_animations(self.right_spritesheet),
            "idle": self.load_animations(self.left_spritesheet)  # Use left as idle
        }

        self.image = self.animations[self.facing][0]
        self.removed = False
        self.asked_question = False
        
        # Special dialogue for Nanay
        self.dialogue = [
            "Hello, anak! How are you today?",
            "Have you eaten already?",
            "Don't forget to do your homework!"
        ]

        self.tasks = [
            {"item": "Milk", "reward": 10, "penalty": -5},
            {"item": "Bread", "reward": 5, "penalty": -3},
            {"item": "Toyo", "reward": 10, "penalty": -5},
            {"item": "Suka", "reward": 10, "penalty": -5},
            {"item": "Rice", "reward": 10, "penalty": -5},
            {"item": "Eggs", "reward": 7, "penalty": -4}
        ]
        self.current_task = None

        self.item_prices = {
            "Milk": 10,
            "Bread": 5,
            "Toyo": 8,
            "Suka": 8,
            "Rice": 8,
            "Eggs": 15
    }
        
   

    def load_animations(self, spritesheet):
        animations = [
            spritesheet.get_sprite(i * TILESIZE, 0, self.width, self.height)
            for i in range(4)
        ]
        return animations
    
    def update(self):
        if not self.removed:
            self.movement()
            self.animate()
            self.detect_player()

    def movement(self):
        # Nanay moves around more randomly
        if self.idle:
            if pygame.time.get_ticks() - self.idle_time > 3000:
                self.idle = False
                self.direction = random.choice(['left', 'right'])
    
    def animate(self):
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
        if self.removed or self.asked_question:
            return

        player_x, player_y = self.game.player.rect.x, self.game.player.rect.y
        distance_x = abs(self.rect.x - player_x)
        distance_y = abs(self.rect.y - player_y)

        if distance_x + distance_y <= 2 * TILESIZE:
            if not self.current_task:
                self.assign_task()

            if self.current_task:  # ✅ Only access if task is assigned
                item = self.current_task['item']
                self.game.show_task_dialogue(
                    f"Anak, please buy me some {item} from the store.",
                    self,
                    ["Yes"],  # Only provide the "Yes" option
                    "Yes",  # Correct answer is always "Yes"
                    "Thank you for accepting the task!",
                    "Maybe next time."  # Provide failure response
                )
                self.asked_question = True

    def assign_task(self):
        if not self.current_task:
            self.current_task = random.choice(self.tasks)
            print(f"Nanay assigned a new task: {self.current_task}")  # Debugging step

    def complete_task(self, player):
        if self.current_task:
            task_item = self.current_task['item']
            penalty = self.current_task['penalty']
            
            if player.has_item(task_item):
                print("Nanay: Thank you for the item!")
                player.remove_item(task_item)
            else:
                player.coins += penalty
                print(f"Nanay: That's not what I asked for! You lost {abs(penalty)} coins.")
            
            # Clear task after completion
            self.current_task = None

    def check_task_completion(self, item):
        # ✅ Skip check if item is None (during reset)
        if item is None:
            return
        
        if self.current_task and item == self.current_task['item']:
            conversation = "Thank you for completing the task!"
            self.game.task_success = True
            self.game.task_in_progress = False
            self.game.current_task = None

            # ✅ Clear task ONLY after checking
            self.current_task = None
            self.game.show_task_dialogue(
                conversation,
                self,
                ["Okay"],
                "Okay",
                None,
                None
            )
        else:
            # ✅ Only show this if the player actively interacts (not during reset)
            if self.game.task_in_progress:
                conversation = "You haven't completed the task yet. Try again!"
                self.game.show_task_dialogue(
                    conversation,
                    self,
                    ["Okay"],
                    "Okay",
                    None,
                    None
                )
