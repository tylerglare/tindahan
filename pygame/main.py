import pygame
from sprites import *
from config import *
from pygame import mixer #from pygame library
import sys
import json

class Game:
    def __init__(self):
        pygame.init()
        print(f"Screen size: {WIN_WIDTH}x{WIN_HEIGHT}")
        self.scaled_width = WIN_WIDTH
        self.scaled_height = WIN_HEIGHT
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('PressStart2P-Regular.ttf', 32)
        self.camera_surface = pygame.Surface((CAM_WIDTH, CAM_HEIGHT))
        self.running = True
        
        self.character_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/JUNJUN IDLE RIGHT.png')
        self.mainwalkright_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/JUNJUN WALK RIGHT.png')
        self.mainwalkleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/JUNJUN WALK LEFT.png')
        self.house_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/BAHAY.png')
        self.house2_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/BAHAY2.png')
        self.tree_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/tree.png')
        self.road1_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/road1.png')
        self.road2_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/road2.png')
        self.road3_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/road3.png')
        self.road4_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/road4.png')
        self.road5_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/road5.png')
        self.road6_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/road6.png')
        self.terrain_spritesheet = Spritesheet('img/terrain.png')
        self.npcwalkright_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/TAMBAY1 WALK RIGHT.png')
        self.npcwalkleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/TAMBAY1 WALK LEFT.png')
        self.npcidle_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/TAMBAY1 IDLE RIGHT.png')
        self.npc1walkright_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/BATA1 WALK RIGHT.png')
        self.npc1walkleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/BATA1 WALK LEFT.png') #corrected a typo
        self.npc1idle_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/BATA1 IDLE RIGHT.png')
        self.attack_spritesheet = Spritesheet('img/attack.png')
        self.intro_background = pygame.image.load('img/MENUSTORE.png')
        self.intro_background = pygame.transform.scale(self.intro_background, (800, 512))
        self.go_background = pygame.image.load('img/gameover.png')
        self.questions = self.load_questions()

        mixer.music.load('Audio.mp3')
        mixer.music.play(-1)#0 if one time play, -1 for loop
        mixer.music.set_volume(1.0)
        self.is_muted = False
        self.previous_volume = 1.0
        self.target_volume = 1.0
        

    def load_questions(self):
        with open('questions.json', 'r') as file:
            data = json.load(file)
        return data

    def createTilemap(self):
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                Ground(self, j, i)
                #if column == "H":
                 #   Block(self, j, i)
                if column == "T":
                    Block2(self, j, i)
                if column in ["H" , "G"]:
                    Block(self, j, i, column)
                if column in ['1', '2', '3', '4', '5', '6']:
                    Road(self, j, i, int(column)) 
                if column == "N":
                    NPC(self, j, i, name="Tambay", difficulty="easy")
                if column == "A":
                    NPC(self, j, i, name="Tambay", difficulty="average")  # Average NPC
                if column == "K":
                    NPC(self, j, i, name="Tambay", difficulty="hard")  # Hard NPC
                if column == "B":
                    NPC(self, j, i, name="Bata", difficulty="easy")  # Bata NPC
                if column == 'P':
                    self.player = Player(self, j, i)
                

    def new(self):
        #a new game starts
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.npcs = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates() 

        self.createTilemap()   

        map_width = len(tilemap[0]) * TILESIZE
        map_height = len(tilemap) * TILESIZE

    # Initialize the camera with the full map size
        self.camera = Camera(map_width, map_height)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.VIDEORESIZE:
            # Update window size and scale graphics
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.scaled_width = event.w
                self.scaled_height = event.h

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player.facing == 'up':
                        Attack(self, self.player.rect.x, self.player.rect.y - TILESIZE)
                    if self.player.facing == 'down':
                        Attack(self, self.player.rect.x, self.player.rect.y + TILESIZE)
                    if self.player.facing == 'left':
                        Attack(self, self.player.rect.x - TILESIZE, self.player.rect.y)
                    if self.player.facing == 'right':
                        Attack(self, self.player.rect.x + TILESIZE, self.player.rect.y)
                if event.key == pygame.K_f:  # Toggle fullscreen
                    self.toggle_fullscreen()
                if event.key == pygame.K_q:  # Show random question
                    question_data = self.get_random_question()
                    self.show_question(question_data['conversation'], question_data['question'], None, question_data['choices'], question_data['correct_answer'])

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.scaled_width, self.scaled_height), pygame.RESIZABLE)

    def show_question(self, conversation, question, npc, choices, correct_answer):
        question_box = pygame.Rect(WIN_WIDTH // 4, WIN_HEIGHT // 4, WIN_WIDTH // 2, 100)
        font = pygame.font.Font(Font, 15)
        text = font.render(conversation, True, WHITE)
        text_rect = text.get_rect(center=question_box.center)
        
        buttons = []
        button_width = 200
        button_height = 40
        button_x = WIN_WIDTH // 3
        button_y = WIN_HEIGHT // 2

        next_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        next_button_text = font.render("Next", True, WHITE)
        next_button_text_rect = next_button_text.get_rect(center=next_button_rect.center)

        running = True
        show_conversation = True

        while running:
            self.screen.fill(BLACK, question_box)
            pygame.draw.rect(self.screen, WHITE, question_box, 2)
            self.screen.blit(text, text_rect)
            
            if show_conversation:
                pygame.draw.rect(self.screen, BLUE, next_button_rect)
                self.screen.blit(next_button_text, next_button_text_rect)
            else:
                for button, choice in buttons:
                    pygame.draw.rect(self.screen, BLUE, button)
                    choice_text = font.render(choice, True, WHITE)
                    choice_text_rect = choice_text.get_rect(center=button.center)
                    self.screen.blit(choice_text, choice_text_rect)
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if show_conversation and next_button_rect.collidepoint(event.pos):
                        show_conversation = False
                        text = font.render(question, True, WHITE)
                        text_rect = text.get_rect(center=question_box.center)
                        for i, choice in enumerate(choices):
                            button_rect = pygame.Rect(button_x, button_y + i * (button_height + 10), button_width, button_height)
                            buttons.append((button_rect, choice))
                    elif not show_conversation:
                        for button, choice in buttons:
                            if button.collidepoint(event.pos):
                                print(f"Player chose: {choice}")
                                if choice == correct_answer:
                                    self.player.coins += 1  # Add coin for correct answer
                                else:
                                    self.player.coins -= 1  # Subtract coin for incorrect answer
                                print(f"Coins: {self.player.coins}")  # Debug print
                                if npc:
                                    npc.return_to_spawn()  # Call the return_to_spawn method on the NPC
                                running = False
            
            pygame.time.delay(100)

    def get_random_question(self):
        return random.choice(self.questions)

    def update(self):
        #game loop updates
        self.all_sprites.update()
        self.camera.update(self.player)
            

    def draw(self):
        # Clear camera surface
        self.camera_surface.fill(BLACK)

        # Draw sprites to the camera surface
        for sprite in self.all_sprites:
            self.camera_surface.blit(sprite.image, self.camera.apply(sprite))

        # Scale the camera surface to match the resized window size
        scaled_surface = pygame.transform.scale(self.camera_surface, (self.scaled_width, self.scaled_height))
        
        # Blit the scaled surface to the screen
        self.screen.blit(scaled_surface, (0, 0))

        # Display the coin count
        self.display_coin_count()

        pygame.display.update()
        
    def display_coin_count(self):
        coin_text = self.font.render(f'Coins: {self.player.coins}', True, WHITE)
        self.screen.blit(coin_text, (1, 1))

    def main(self):
        #game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        text = self.font.render('Game Over', True, WHITE)
        text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))

        restart_button = Button(10, WIN_HEIGHT - 60, 120, 50, WHITE, BLACK, 'Restart', 32)

        for sprite in self.all_sprites:
            sprite.kill()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed):
                self.new()
                self.main()

            self.screen.blit(self.go_background, (0, 0))
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_button.image, restart_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def intro_screen(self):
        intro = True

        title = self.font.render('Tindahan ni Aling Nena', True, BLACK)
        self.title_rect = title.get_rect(x=10, y=10)

        play_button = Button(281, 120, 240, 50,  WHITE, BLACK, 'Play', 26, 0)
        options_button = Button(281, 180, 240, 50, WHITE, BLACK, 'Options', 26, 0)
        exit_button = Button(281, 250, 240, 50, WHITE, BLACK, 'Exit', 26, 0)
        credits_button = Button(281, 310, 240, 50, WHITE, BLACK, 'Credits', 26, 0)
        
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
            #self.screen.blit(title, title_rect)
            
            if options_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False

            if exit_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
                self.running = False
                pygame.quit()
                sys.exit()
            
            if credits_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(play_button.image, play_button.rect)
            self.screen.blit(options_button.image, options_button.rect)
            self.screen.blit(exit_button.image, exit_button.rect)  # Fixed typo here
            self.screen.blit(credits_button.image, credits_button.rect)
            
            self.clock.tick(FPS)
            pygame.display.update()
            
    def options_screen(self):
        options = True
        font = pygame.font.Font('PressStart2P-Regular.ttf',27)
        title_text = font.render('Options',True,WHITE)

        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen.get_width()//2
        title_rect.top = 30
        
        self.OCbackground = pygame.image.load('img/Sari.png')
        self.OCbackground = pygame.transform.scale(self.OCbackground, (800, 512))
        
        mute_button = Button(281,280,240, 50, WHITE, BLACK,'Mute',21, 0 )
        back_button = Button(281, 410, 240, 50 , WHITE, BLACK, 'Back', 27, 0)
        
        muted = False
        previous_volume = mixer.music.get_volume()

        slider_x = 195 #decrease to move left, increase to move right
        slider_y = 180 #decrease to move up, increase to move down
        slider_width = 400 #decrease horizontal line,  increase horizontal line
        slider_height = 5  #decrease to shorten size
        handle_width = 20 
        handle_height = 20 

        current_volume = previous_volume
        slider_handle_x = slider_x + current_volume * slider_width

        dragging_slider = False
        hitbox_padding = 40 #increase hitbox size 

        while options:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    options = False
                    self.running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                  if(slider_handle_x-hitbox_padding <= event.pos[0]<= slider_handle_x + handle_width + handle_height and
                       slider_y - hitbox_padding <= event.pos[1] <= slider_y + slider_height + hitbox_padding):
                       dragging_slider = True
                  elif mute_button.rect.collidepoint(event.pos):
                     if not muted:
                            previous_volume = current_volume
                            previous_slider_handle_x = slider_handle_x
                            mixer.music.set_volume(0.0)
                            current_volume = 0.0
                            slider_handle_x = slider_x
                            mute_button.update_text('Unmute')
                            muted = True
                     else:
                            mixer.music.set_volume(previous_volume)
                            current_volume = previous_volume
                            slider_handle_x = previous_slider_handle_x
                            mute_button.update_text('Mute')
                            muted = False

                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging_slider = False
                elif event.type == pygame.MOUSEMOTION and dragging_slider and not muted:
                    new_x = max(slider_x,min(slider_x + slider_width - handle_width,event.pos[0] - handle_width//2))
                    slider_handle_x = new_x
                    current_volume = (slider_handle_x -slider_x)/(slider_width - handle_height )
                    mixer.music.set_volume(current_volume)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            

            volume_font = pygame.font.Font('PressStart2P-Regular.ttf',20)
            self.screen.blit(self.OCbackground, (0,0))
            volume_text = volume_font.render(f'Volume: {int(current_volume*100)*(not muted)}%',True,WHITE)
            volume_text_rect = volume_text.get_rect()
            volume_text_rect.centerx = self.screen.get_width()//2
            volume_text_rect.top = 210
         
            self.screen.blit(title_text, title_rect)
            mute_button.draw(self.screen)
            self.screen.blit(back_button.image, back_button.rect)
            
            pygame.draw.rect(self.screen,RED,(slider_x,slider_y,slider_width,slider_height))

            pygame.draw.rect(self.screen,WHITE,(slider_handle_x, slider_y - handle_height//2, handle_width, handle_height))
            
            self.screen.blit(volume_text, volume_text_rect)

            if back_button.is_pressed(mouse_pos, mouse_pressed):
                options =False
            
            self.clock.tick(FPS)
            pygame.display.update()
            
    def credits_screen(self):
        credits = True
        title_font = pygame.font.Font('PressStart2P-Regular.ttf',27)
        credits_font = pygame.font.Font('PressStart2P-Regular.ttf', 20)
        title_text = title_font.render('Credits', True, WHITE)

        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen.get_width()//2
        title_rect.top = 13

        back_button = Button(281,450,240,50, WHITE, BLACK,'Back', 27, 0)

        credits_text = [
            'Game by Team Tindahan',
            'Team Tindahan:',
            '           Rana Carlos',
            '           Terrylle Augie Gonatice',
            '           Ma Rhoabel Sanchez',
            '           John Dharell Marcos',
            'Art by Rana Carlos',
            'Music by Eraserheads',
            '           Thanks for playing',
        ]

        while credits:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    credits = False
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if back_button.is_pressed(mouse_pos, mouse_pressed):
                credits = False

            self.screen.fill(BLACK)
            self.screen.blit(title_text, title_rect)

            y_offset = 60

            for line in credits_text:
                credits_line = credits_font.render(line, True, WHITE)
                self.screen.blit(credits_line, (12, y_offset))
                y_offset += 45

            self.screen.blit(back_button.image, back_button.rect)

            self.clock.tick(FPS)
            pygame.display.update()


g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

mixer.music.stop()
pygame.quit()
sys.exit()
