import pygame
from sprites import *
from config import *
from ui import DialogueBox, QuestionBox
import sys
import json
from pygame import mixer

class Game:
    def __init__(self):
        pygame.init()
        print(f"Screen size: {WIN_WIDTH}x{WIN_HEIGHT}")
        self.scaled_width = WIN_WIDTH
        self.scaled_height = WIN_HEIGHT
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('PressStart2P-Regular.ttf', 32)
        self.camera_surface = pygame.Surface((CAM_WIDTH, CAM_HEIGHT))
        self.running = True
        self.font_button = 16
        
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
        self.npcw1alkleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/BATA1 WALK LEFT.png')
        self.npc1idle_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/BATA1 IDLE RIGHT.png')
        self.alingnenaleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/ALING NENA IDLE LEFT.png')
        self.alingnenaright_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/ALING NENA IDLE RIGHT.png')
        self.nanayleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/NANAY IDLE LEFT.png')
        self.nanayright_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/NANAY IDLE RIGHT.png')

        self.attack_spritesheet = Spritesheet('img/attack.png')
        self.intro_background = pygame.image.load('img/MENU.png')
        self.intro_background = pygame.transform.scale(self.intro_background, (800, 512))
        self.go_background = pygame.image.load('img/gameover.png')
        self.questions = self.load_questions()

        # Initialize active dialogue and question box
        mixer.music.load('Audio.mp3')  # Initialize background music
        mixer.music.play(-1)  # Loop music
        mixer.music.set_volume(1.0)
        self.is_muted = False
        self.previous_volume = 1.0

        self.current_task = None
        self.task_success = False
        self.task_in_progress = False
        self.loop_count = 0  # Add a loop counter

    def load_questions(self):
        with open('questions.json', 'r') as file:
            data = json.load(file)
        return data
    
    def show_task_dialogue(self, conversation, npc, choices, correct_answer, success_response, failure_response):
        self.active_dialogue = DialogueBox(self.screen, self.player, npc, 'img/DBOX.png', 'img/PROFILE1.png', 700, 250)
        
        # Use the show_dialogue method from DialogueBox
        self.active_dialogue.show_dialogue(
            npc,
            conversation,
            "Do you want to proceed?",
            choices,
            correct_answer,
            {
                "correct": [success_response],
                "wrong": [failure_response]
            }
        )

        # Reward the player with 20 coins if the task is accepted
        if correct_answer == "Yes":
            self.player.coins += 19
            print(f"Task accepted. Coins: {self.player.coins}")
        
    def createTilemap(self):
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                Ground(self, j, i)
                if column == "T":
                    Block2(self, j, i)
                if column in ["H" , "G", "Y", "L"]:
                    Block(self, j, i, column)
                if column in ['1', '2', '3', '4', '5', '6']:
                    Road(self, j, i, int(column)) 
                if column == "X":
                    NPC(self, j, i, name="Teacher", difficulty="easy")
                if column == "C":
                    NPC(self, j, i, name="Teacher", difficulty="average")
                if column == "R":
                    NPC(self, j, i, name="Teacher", difficulty="hard")
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
                if column == "S":
                    School(self, j, i)
                if column == "M":
                    Shop(self, j, i)
                if column == "Z":
                    Zone(self, j, i)
                if column == "E":  # Aling Nena
                    AlingNena(self, j, i)
                if column == "F":  # Nanay
                    Nanay(self, j, i)

    def new(self):
        # a new game starts
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

        self.current_task = None
        self.task_success = False
        self.task_in_progress = False


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
                
                # Update the camera surface to match the new screen size
                self.camera_surface = pygame.Surface((self.scaled_width, self.scaled_height))
                
                # Scale the intro background to match the new screen size
                self.intro_background = pygame.transform.scale(self.intro_background, (self.scaled_width, self.scaled_height))

                # Redraw the screen after resizing
                self.draw()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Show random question
                    question_data = self.get_random_question()
                    self.show_question(question_data['conversation'], question_data['question'], None, question_data['choices'], question_data['correct_answer'])

    def show_question(self, conversation, question, npc, choices, correct_answer, responses):
        self.active_dialogue = DialogueBox(self.screen, self.player, npc, 'img/DBOX.png', 'img/PROFILE1.png', 700, 250)
        self.active_dialogue.show_dialogue(npc, conversation, question, choices, correct_answer, responses)

    def get_random_question(self):
        difficulty = "easy" if self.loop_count == 0 else "average" if self.loop_count == 1 else "hard"
        return random.choice(self.questions[difficulty])
    
    def handle_nanay_interaction(self):
        if not self.task_in_progress:
            self.assign_new_task()
        else:
            self.check_task_completion()

    def assign_new_task(self):
        self.current_task = {
            'item': 'Milk',  # Example task
            'cost': 10
        }
        self.task_in_progress = True
        conversation = f"Please buy {self.current_task['item']} from Aling Nena for {self.current_task['cost']} coins."
        self.show_dialogue("Nanay", conversation)

    def check_task_completion(self):
        if self.task_success:
            conversation = "Thank you for completing the task!"
            self.task_success = False
            self.task_in_progress = False
            self.current_task = None
            self.player.coins += 5  # Reward for success
        else:
            conversation = "You haven't completed the task yet. Try again!"
        self.show_dialogue("Nanay", conversation)

    def handle_alingnena_interaction(self):
        nanay = next((npc for npc in self.npcs if isinstance(npc, Nanay)), None)
        aling_nena = next((npc for npc in self.npcs if isinstance(npc, AlingNena)), None)

        if nanay and nanay.current_task and aling_nena:
            task = nanay.current_task
            item = task['item']
            cost = aling_nena.item_prices.get(item, 0)

            if self.player.coins >= cost:
                self.player.coins -= cost
                self.player.add_item(item)
                self.show_task_dialogue(
                    f"You bought {item} for {cost} coins!",
                    aling_nena, 
                    ["Okay"],
                    None,
                    None,
                    None
                )
                self.reset_game()
                nanay.check_task_completion(item)
                
            else:
                self.show_task_dialogue(
                    "You don't have enough coins!",
                    aling_nena,
                    ["Okay"],
                    None,
                    None,
                    None
                )
                self.reset_game()


    def reset_game(self):
        nanay = next((npc for npc in self.npcs if isinstance(npc, Nanay)), None)
        
        # Store the last task
        last_task = self.current_task  
        
        if nanay:
            # Reset player to spawn beside Nanay
            self.player.rect.x = nanay.rect.x + TILESIZE
            self.player.rect.y = nanay.rect.y
            self.player.x = nanay.rect.x + TILESIZE
            self.player.y = nanay.rect.y

        # Reset game state
        self.current_task = None
        self.task_success = False
        self.task_in_progress = False

        # Reset NPC state
        for npc in self.npcs:
            npc.asked_question = False

        # Redraw the screen to avoid graphical glitches
        self.draw()

        # Ensure Nanay checks the last task before assigning a new one
        if nanay:
            nanay.check_task_completion(last_task)  # Pass last task instead of None
            nanay.assign_task()

        # Handle game loop progression
        self.loop_count += 1
        print(f"Loop Count: {self.loop_count}")  # Debugging step

        # Check for game-over state
        if self.loop_count >= 3:
            print("Game Over!")
            self.game_over()  # Transition to game-over screen
        else:
            self.playing = True  # Continue playing


    def handle_event(self, event):
        if event.type == pygame.USEREVENT + 1:
            nanay = next((npc for npc in self.npcs if isinstance(npc, Nanay)), None)
            if nanay and self.current_task:
                # ✅ Let Nanay check the task
                nanay.check_task_completion(self.current_task['item'])

                # ✅ Now clear the task AFTER checking
                self.current_task = None
                self.task_success = False
                self.task_in_progress = False

            # ✅ Stop the timer after one call
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)




    def update(self):
        # game loop updates
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw(self):
        # Clear camera surface with the correct background
        self.camera_surface.blit(self.intro_background, (0, 0))  # Changed to intro_background

        # Draw sprites to the camera surface
        for sprite in self.all_sprites:
            self.camera_surface.blit(sprite.image, self.camera.apply(sprite))

        # Scale the camera surface to match the resized window size
        scaled_surface = pygame.transform.scale(self.camera_surface, (self.scaled_width, self.scaled_height))
        
        # Blit the scaled surface to the screen
        self.screen.blit(scaled_surface, (0, 0))

        # Display the coin count
        self.display_coin_count()

        
        pygame.display.flip()

    def display_coin_count(self):
        coin_text = self.font.render(f'{self.player.coins}', True, BLACK)
        coin_icon = pygame.image.load("img/TINDAHAN CHARACTERS/coin.png").convert_alpha()
        coin_icon = pygame.transform.scale(coin_icon, (48, 48))

        # Adjust based on current window size
        screen_width = self.screen.get_width()
        self.screen.blit(coin_icon, (screen_width - 100, 10))
        self.screen.blit(coin_text, (screen_width - 170, 20))

    def main(self):
        # game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        text = self.font.render('Game Over', True, WHITE)
        text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))

        restart_button = Button(10, WIN_HEIGHT - 60, 120, 50, 'c:\\Users\\This PC\\OneDrive\\Documents\\054\\TindahanGame\\img\\ABUT.png', 'Restart', 32, WHITE)

        for sprite in self.all_sprites:
            sprite.kill()

        while self.running:
            self.screen.blit(self.go_background, (0, 0))
            self.screen.blit(text, text_rect)
            restart_button.draw(self.screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.is_pressed(event.pos, pygame.mouse.get_pressed()):
                        self.new()
                        self.main()

    def options_screen(self):
            options = True
            button_image_path = 'c:\\Users\\This PC\\OneDrive\\Documents\\054\\TindahanGame\\img\\ABUT.png'
            font = pygame.font.Font('PressStart2P-Regular.ttf', 27)
            title_text = font.render('Options', True, WHITE)
            title_rect = title_text.get_rect(centerx=self.screen.get_width() // 2, top=30)
            
            self.OCbackground = pygame.image.load('img/MENUBG.png')
            self.OCbackground = pygame.transform.scale(self.OCbackground, (self.scaled_width, self.scaled_height))
            mute_button = Button(281, 280, 240, 50, button_image_path, WHITE, 'MUTE', self.font_button)
            back_button = Button(281, 410, 240, 50, button_image_path, WHITE, 'BACK', self.font_button)

            slider_x, slider_y, slider_width, slider_height = 195, 180, 400, 5
            handle_width, handle_height = 20, 20
            current_volume = mixer.music.get_volume()
            slider_handle_x = slider_x + current_volume * slider_width
            dragging_slider = False

            while options:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        options = False
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if slider_handle_x - 40 <= event.pos[0] <= slider_handle_x + handle_width + 40 and \
                        slider_y - 40 <= event.pos[1] <= slider_y + slider_height + 40:
                            dragging_slider = True
                        elif mute_button.rect.collidepoint(event.pos):
                            if not self.is_muted:
                                self.previous_volume = current_volume
                                mixer.music.set_volume(0.0)
                                mute_button.update_text('Unmute')
                                self.is_muted = True
                            else:
                                mixer.music.set_volume(self.previous_volume)
                                mute_button.update_text('Mute')
                                self.is_muted = False
                    elif event.type == pygame.MOUSEBUTTONUP:
                        dragging_slider = False
                    elif event.type == pygame.MOUSEMOTION and dragging_slider and not self.is_muted:
                        slider_handle_x = max(slider_x, min(slider_x + slider_width - handle_width, event.pos[0]))
                        current_volume = (slider_handle_x - slider_x) / slider_width
                        mixer.music.set_volume(current_volume)

                self.screen.blit(self.OCbackground, (0, 0))
                self.screen.blit(title_text, title_rect)
                mute_button.draw(self.screen)
                back_button.draw(self.screen)

                pygame.draw.rect(self.screen, RED, (slider_x, slider_y, slider_width, slider_height))
                pygame.draw.rect(self.screen, WHITE, (slider_handle_x, slider_y - handle_height // 2, handle_width, handle_height))

                if back_button.is_pressed(pygame.mouse.get_pos(), pygame.mouse.get_pressed()):
                    options = False

                self.clock.tick(FPS)
                pygame.display.update()

    def credits_screen(self):
            credits = True
            title_font = pygame.font.Font('PressStart2P-Regular.ttf', 27)
            credits_font = pygame.font.Font('PressStart2P-Regular.ttf', 20)
            title_text = title_font.render('Credits', True, WHITE)
            title_rect = title_text.get_rect(centerx=self.screen.get_width() // 2, top=13)

            self.OCbackground = pygame.image.load('img/MENUBG.png')
            self.OCbackground = pygame.transform.scale(self.OCbackground, (CAM_WIDTH, CAM_HEIGHT))

            button_image_path = 'c:\\Users\\This PC\\OneDrive\\Documents\\054\\TindahanGame\\img\\ABUT.png'
            back_button = Button(281, 450, 240, 50, button_image_path, BLACK, 'Back', self.font_button, 0)
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

                self.screen.blit(self.OCbackground, (0, 0))
                self.screen.blit(title_text, title_rect)

                y_offset = 60
                for line in credits_text:
                    credits_line = credits_font.render(line, True, WHITE)
                    self.screen.blit(credits_line, (12, y_offset))
                    y_offset += 45

                back_button.draw(self.screen)
                if back_button.is_pressed(pygame.mouse.get_pos(), pygame.mouse.get_pressed()):
                    credits = False

                self.clock.tick(FPS)
                pygame.display.update()

    def intro_screen(self):
        intro = True

        title = self.font.render('Tindahan ni Aling Nena', True, BLACK)
        self.title_rect = title.get_rect(x=10, y=10)

        button_image_path = 'c:\\Users\\This PC\\OneDrive\\Documents\\054\\TindahanGame\\img\\ABUT.png'
        play_button = Button(281, 120, 240, 50, button_image_path, WHITE, 'Play', self.font_button)
        options_button = Button(281, 180, 240, 50, button_image_path, WHITE, 'Options', self.font_button)
        exit_button = Button(281, 250, 240, 50, button_image_path, WHITE, 'Exit', self.font_button)
        credits_button = Button(281, 310, 240, 50, button_image_path, WHITE, 'Credits',self.font_button)
        
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False

                if event.type == pygame.VIDEORESIZE:
                    # Update window size and scale graphics
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.scaled_width = event.w
                    self.scaled_height = event.h
                    
                    # Scale the intro background to match the new screen size
                    self.intro_background = pygame.transform.scale(self.intro_background, (self.scaled_width, self.scaled_height))

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:  # Toggle fullscreen
                        self.toggle_fullscreen()

                        # Scale the intro background to match the new screen size
                        self.intro_background = pygame.transform.scale(self.intro_background, (self.scaled_width, self.scaled_height))

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
            
            if options_button.is_pressed(mouse_pos, mouse_pressed):
                self.options_screen()

            if exit_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
                self.running = False
                pygame.quit()
                sys.exit()
            
            if credits_button.is_pressed(mouse_pos, mouse_pressed):
                self.credits_screen()

            self.screen.blit(self.intro_background, (0, 0))
            play_button.draw(self.screen)
            options_button.draw(self.screen)
            exit_button.draw(self.screen)
            credits_button.draw(self.screen)
            
            self.clock.tick(FPS)
            pygame.display.update()

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()
