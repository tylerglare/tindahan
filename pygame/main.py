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
        
        self.map_width = len(tilemap[0]) * TILESIZE
        self.map_height = len(tilemap) * TILESIZE
        # Initialize attributes for sprites and NPCs
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.npcs = pygame.sprite.LayeredUpdates()  # Initialize self.npcs


        self.aling_nena = None  # Initialize self.aling_nena as None
        self.player = None  # Initialize self.player as None

        # Other initializations...
        self.mainidleright_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/JUNJUN IDLE RIGHT.png')
        self.mainidleleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/JUNJUN IDLE LEFT.png')
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
        self.task_in_progress = False
        self.loop_count = 0  # Add a loop counter
        self.difficulty = "easy"

    def load_questions(self):
        with open('questions.json', 'r') as file:
            data = json.load(file)
        return data
    
    def show_task_dialogue(self, conversation, npc, choices, correct_answer, success_response, failure_response):
        self.active_dialogue = DialogueBox(
        self,  # ✅ Pass the game instance here
        self.screen,
        self.player,
        npc,
        'img/DBOX.png',
        'img/PROFILE1.png',
        700,
        250
    )
        
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
            self.player.coins += 10
            print(f'{success_response}')
            print(f"Task accepted. Coins: {self.player.coins}")
        else:
            print("Task rejected.")
        
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
                    print(f"Spawning Teacher at ({j}, {i})")  # DEBUG
                    difficulty = "easy" if self.loop_count == 0 else "average" if self.loop_count == 1 else "hard"
                    NPC(self, j, i, name="Teacher", difficulty=difficulty)
                if column == "C":
                    print(f"Spawning Tambay at ({j}, {i})")  # DEBUG
                    difficulty = "easy" if self.loop_count == 0 else "average" if self.loop_count == 1 else "hard"
                    NPC(self, j, i, name="Tambay", difficulty=difficulty)
                if column == "B":
                    difficulty = "easy" if self.loop_count == 0 else "average" if self.loop_count == 1 else "hard"
                    NPC(self, j, i, name="Bata", difficulty=difficulty)
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
                    print(f"Aling Nena created at ({j}, {i}) and added to self.npcs")
                if column == "F":  # Nanay
                    Nanay(self, j, i)

    def new(self):
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.npcs = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.createTilemap()  # Recreate the game world

        map_width = len(tilemap[0]) * TILESIZE
        map_height = len(tilemap) * TILESIZE

        # Initialize the camera with the full map size
        self.camera = Camera(map_width, map_height)

        self.current_task = None
        self.task_success = False
        self.task_in_progress = False
        print(f"Loop count remains: {self.loop_count}")  # Debugging step

        # Assign difficulty to NPCs based on the current loop
        difficulty = "easy" if self.loop_count == 0 else "average" if self.loop_count == 1 else "hard"
        for npc in self.npcs:
            npc.difficulty = difficulty  # Dynamically set NPC difficulty
            print(f"Assigned difficulty '{difficulty}' to NPC: {npc.name}")  # Debugging step

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
                    self.show_question(question_data['conversation'], question_data['question'], None, question_data['choices'], question_data['correct_answer'], question_data['difficulty'])

    def show_question(self, conversation, question, npc, choices, correct_answer, responses, difficulty):
       
        self.active_dialogue = DialogueBox(
        self,  # ✅ Pass the game instance here
        self.screen,
        self.player,
        npc,
        'img/DBOX.png',
        'img/PROFILE1.png',
        700,
        250
    )
        self.active_dialogue.show_dialogue(npc, conversation, question, choices, correct_answer, responses)

   

    def get_random_question(self):
        difficulty = "easy" if self.loop_count == 0 else "average" if self.loop_count == 1 else "hard"
        return (self.questions[difficulty])
    
    def handle_nanay_interaction(self):
        print("handle_nanay_interaction called")  # Debugging step
        print(f"Task in progress: {self.task_in_progress}")  # Debugging step

        nanay = next((npc for npc in self.npcs if isinstance(npc, Nanay)), None)
        if not self.task_in_progress and nanay:
            # Assign a new task directly
            nanay.assign_task()  # Delegate task assignment to Nanay
            self.current_task = nanay.current_task
            print(f"Assigned new task: {self.current_task}")  # Debugging step
            self.task_in_progress = True
            conversation = f"Please buy {self.current_task['item']} from Aling Nena for {self.current_task['cost']} coins."
            self.show_dialogue("Nanay", conversation)
        elif self.task_in_progress:
            # If the player says "Yes" to the task
            response = "Thank you for accepting the task!"
            self.show_dialogue("Nanay", response)
            # Task is now active, proceed to buying/checking state next
        else:
            self.check_task_completion()

    def check_task_completion(self):
        if self.task_success:
            print("Task successfully completed!")  # Debugging step
            conversation = "Thank you for completing the task!"
            self.task_success = False
            self.task_in_progress = False
            self.current_task = None
            self.player.coins += 5  # Reward for success
        else:
            conversation = "You haven't completed the task yet. Try again!"
        self.show_dialogue("Nanay", conversation)

    def handle_alingnena_interaction(self):
        print("handle_alingnena_interaction called")
        nanay = next((npc for npc in self.npcs if isinstance(npc, Nanay)), None)
        aling_nena = next((npc for npc in self.npcs if isinstance(npc, AlingNena)), None)

        if nanay and nanay.current_task and aling_nena:
            print(f"Interacting with Aling Nena. Current task: {nanay.current_task}")  # Debugging step
            task = nanay.current_task
            item = task['item']
            print(f"Item to buy: {item}")
            cost = aling_nena.item_prices.get(item, 0)

            if self.player.coins >= cost:
                self.player.coins -= cost
                self.player.add_item(item)
                
                self.show_task_dialogue(
                    f"You bought {item} for {cost} coins",
                    aling_nena,
                    ["Okay"],  # Just an "Okay" button
                    "Okay",    # No logic needed since it's just a confirmation
                    None,
                    None
                )
                nanay.check_task_completion(item)
                self.task_success = True 
                print("Task success set to True")
    
                self.reset_game()
            else:
                self.show_task_dialogue(
                    "You don't have enough coins!",
                    aling_nena,
                    ["Okay"],  # Just an "Okay" button
                    "Okay",    # No logic needed since it's just a failure message
                    None,
                    None
                )
                self.game_over()

    def handle_npc_interaction(self, npc):
        # Get the difficulty of the NPC
        difficulty = npc.difficulty

        # Select a random question based on the NPC's difficulty
        question_data = self.get_new_question(npc)

        # Show the question
        self.show_question(
            question_data['conversation'],
            question_data['question'],
            npc,
            question_data['choices'],
            question_data['correct_answer'],
            question_data['responses'],
            difficulty  # Pass the difficulty argument
        )
    def get_new_question(self, npc):
        difficulty = npc.difficulty
        
        if npc.name not in self.asked_questions:
            self.asked_questions[npc.name] = set()

        # Get all questions for the current difficulty
        available_questions = [
            q for q in self.questions[difficulty] 
            if q['question'] not in self.asked_questions[npc.name]
        ]

        if not available_questions:
            # Reset if all questions have been asked
            self.asked_questions[npc.name].clear()
            available_questions = self.questions[difficulty]

        question_data = random.choice(available_questions)

        # Mark question as asked
        self.asked_questions[npc.name].add(question_data['question'])

        return question_data

    def reset_game(self):
        print("reset_game called")  # Debugging step
        print(f"Current task before reset: {self.current_task}")  # Debugging step

        aling_nena = next((npc for npc in self.npcs if isinstance(npc, AlingNena)), None)
        nanay = next((npc for npc in self.npcs if isinstance(npc, Nanay)), None)

       
        # Reset player position (e.g., near Nanay)
        if nanay:
            self.player.rect.x = nanay.rect.x + TILESIZE
            self.player.rect.y = nanay.rect.y
            self.player.x = nanay.rect.x - TILESIZE
            self.player.y = nanay.rect.y
            print(f"Player position reset near Nanay: ({self.player.rect.x}, {self.player.rect.y})")  # Debugging step

        # Reset Aling Nena's position and state
        if aling_nena:
            print(f"Resetting Aling Nena's state. asked_question: {aling_nena.asked_question}, removed: {aling_nena.removed}")
            aling_nena.rect.x = aling_nena.start_x
            aling_nena.rect.y = aling_nena.start_y
            aling_nena.asked_question = False  # Explicitly reset this flag
            aling_nena.removed = False  # Explicitly reset this flag
                
            print(f"Aling Nena position reset: ({aling_nena.rect.x}, {aling_nena.rect.y})")  # Debugging step

        # Reset task-related variables
        self.task_success = False
        self.task_in_progress = False
        self.current_task = None

        # Reset NPC states
        for npc in self.npcs:
            npc.asked_question = False  # Reset any question-related flags
            npc.removed = False  
            if hasattr(npc, 'return_to_spawn'):
                npc.return_to_spawn()       # Reset any removed NPCs

        print("Resetting game state for the next loop...")
        print(f"Current task before reset: {self.current_task}")  # Debugging step

        # Increment the loop count
        self.loop_count += 1
        print(f"Loop count incremented to: {self.loop_count}")  # Debugging step

        # Assign a new task to Nanay AFTER resetting the game state
        

        # Check if the game should end after 3 loops
        if self.loop_count >= 3:
            print("Game Over! Returning to the intro screen.")
            self.intro_screen()
        else:
            print("Game reset complete. Starting the next loop.")

        if nanay:
            nanay.current_task = None  # Clear the previous task
            nanay.assign_task()  # Assign a new task
            self.current_task = nanay.current_task  # Update the game's current task
            print(f"New task assigned: {self.current_task}")  # Debugging step

        

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

    def check_alingnena_interaction(self):
        aling_nena = next((npc for npc in self.npcs if isinstance(npc, AlingNena)), None)
        if aling_nena:  # Ensure Aling Nena exists
            
            if pygame.sprite.collide_rect(self.player, aling_nena):
                return True

        return False

    def run_game_loop(self):
        for _ in range(3):  # Loop 3 times
            print(f"Starting loop {_ + 1}")
            self.new()  # Reset the game state
            print(f"Loop count after reset: {self.loop_count}")
            self.main()  # Run the main game loop
            if self.loop_count == 3:
                self.loop_count = 0
                self.difficulty = 'easy'
            if not self.running == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
                break
            if self.task_success:  # Check if the task was completed successfully
                print("Task completed! Proceeding to the next loop.")
                self.reset_game()  # Reset the game for the next loop
            else:
                print("Task failed or incomplete. Returning to the intro screen.")
                break  # Exit the loop if the task was not completed

        print("All loops completed. Returning to the intro screen.")
        self.intro_screen()
        

    def update(self):
        # Game loop updates
        self.all_sprites.update()
        self.camera.update(self.player)

        if self.loop_count == 0:
            self.difficulty = "easy"
        elif self.loop_count == 1:
            self.difficulty = "average"
        else:
            self.difficulty = "hard"
        nanay = next((npc for npc in self.npcs if isinstance(npc, Nanay)), None)
        if nanay and pygame.sprite.collide_rect(self.player, nanay):
            self.handle_nanay_interaction()
        # Automatically handle interaction with Aling Nena if the player is near
        if self.check_alingnena_interaction():
            print("Player is near Aling Nena.")
            self.handle_alingnena_interaction()

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

        # Display the difficulty level
        self.display_difficulty()

   

        pygame.display.flip()

    def display_coin_count(self):
        coin_text = self.font.render(f'{self.player.coins}', True, BLACK)
        coin_icon = pygame.image.load("img/TINDAHAN CHARACTERS/coin.png").convert_alpha()
        coin_icon = pygame.transform.scale(coin_icon, (48, 48))

        # Adjust based on current window size
        screen_width = self.screen.get_width()
        self.screen.blit(coin_icon, (screen_width - 100, 10))
        self.screen.blit(coin_text, (screen_width - 165, 20))

    def display_difficulty(self):
        # Determine difficulty based on loop_count
        difficulty = "Easy" if self.loop_count == 0 else "Average" if self.loop_count == 1 else "Hard"
        if self.loop_count == 3:
            self.loop_count = 0
            self.difficulty = 'easy'
        # Render the difficulty text
        

        difficulty_text = self.font.render(f"{difficulty}", True, BLACK)
        difficulty_bg = pygame.image.load("img/DBOX.png").convert_alpha()

        if difficulty == "Easy":
            difficulty_text = self.font.render(f"Easy", True, BLACK)
        elif difficulty == "Average":
            difficulty_text = self.font.render(f"Ave", True, BLACK)
        elif difficulty == "Hard":
            difficulty_text = self.font.render(f"Hard", True, BLACK)
        difficulty_bg = pygame.transform.scale(difficulty_bg, (230, 100))
        # Position the text on the screen (top-left corner)
        self.screen.blit(difficulty_bg, (-30, -20))
        self.screen.blit(difficulty_text, (25, 15))
        

    def main(self):
        # game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        print("Game Over! Not enough coins.")
        
        # Display "Game Over" message
        text = self.font.render('Game Over', True, WHITE)
        text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
        pygame.display.flip()
        pygame.time.wait(50)
        # Draw text on the screen
        self.screen.blit(text, text_rect)
          # Show for 1 second before the button appears
        button_image_path = 'c:\\Users\\This PC\\OneDrive\\Documents\\054\\TindahanGame\\img\\ABUT.png'
        # Create restart button
        restart_button = Button(281, 280, 240, 50, button_image_path, WHITE, 'RESTART', self.font_button)
        
        

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.is_pressed(mouse_pos, mouse_pressed):
                        waiting = False
                        self.loop_count = 0
                        self.difficulty = 'easy'
                        self.intro_screen()
            
            # Draw button
            self.screen.fill((0, 0, 0))  # Clear screen before drawing
            self.screen.blit(text, text_rect)
            restart_button.draw(self.screen)
            pygame.display.flip()

    
        self.run_game_loop()

        self.reset_game()
        

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
                        self.loop_count = 0
                        self.difficulty = 'easy'
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
                                mute_button.update_text('UNMUTE')
                                self.is_muted = True
                            else:
                                mixer.music.set_volume(self.previous_volume)
                                mute_button.update_text('MUTE')
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
            self.OCbackground = pygame.transform.scale(self.OCbackground, (self.scaled_width, self.scaled_height))

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

    def how_to_play_screen(self):
        how_to_play = True
        
        # Title setup
        title_font = pygame.font.Font('PressStart2P-Regular.ttf', 27)
        content_font = pygame.font.Font('PressStart2P-Regular.ttf', 10)
        title_text = title_font.render('How to Play', True, WHITE)
        title_rect = title_text.get_rect(centerx=self.screen.get_width() // 2, top=20)
        
        # Background setup
        self.how_to_play_bg = pygame.image.load('img/MENUBG.png')
        self.how_to_play_bg = pygame.transform.scale(self.how_to_play_bg, (self.scaled_width, self.scaled_height))
        
        # Text background setup using a rect
        text_bg_rect = pygame.Rect(
            -50,                      # x position
            0,                      # y position
            890, # width
            500                      # height
        )
        
        # Load and scale the text background image
        text_bg_image = pygame.image.load('img/DBOX.png')
        text_bg_image = pygame.transform.scale(text_bg_image, (text_bg_rect.width, text_bg_rect.height))
        
        # Back button setup
        button_image_path = 'img/ABUT.png'
        back_button = Button(281, 450, 240, 50, button_image_path, WHITE, 'Back', self.font_button)
        margin = 150
        # Scrollable content area setup
        content_area = {
            'x': text_bg_rect.x + margin,
            'y': text_bg_rect.y + margin,
            'width': 600,
            'height': 200,
            'scroll_y': 0,
            'max_scroll': 0,  # Will be calculated based on content
            'scroll_speed': 20
        }
        
        # How to play content - each item is a paragraph
        how_to_play_text = [
            "Welcome to Tindahan ni Aling Nena!",
            "",
            "OBJECTIVE:",
            "Complete tasks by buying items from Aling Nena's store.",
            "",
            "CONTROLS:",
            "- Use A,S,D,W to move your character",
            "- Go near NPCs to interact",
            "- Use MOUSE to select dialogue options",
            "",
            "GAMEPLAY:",
            "1. Talk to Nanay to receive a task",
            "2. Go to Aling Nena's store to buy the requested item",
            "3. Make sure you have enough coins for the purchase",
            "4. Nanay will check if player completed the task",
            "5. Complete three tasks to win the game",
            "",
            "DIFFICULTY:",
            "The game has three difficulty levels:",
            "- Easy: Questions are Easy",
            "           Reward: 1 coin",
            "           Penalty: 3 coins",
            "- Average: Questions are set in Average Difficulty",
             "          Reward: 2 coins",
            "           Penalty: 5 coins",
            "- Hard: Questions are set in Hard Difficulty",
            "           Reward: 3 coins",
            "           Penalty: 7 coins",
            "",
            "TIPS:",
            "- Keep track of your coins",
            "- If you don't have enough coins, the game will end",
            "- Answer questions correctly to earn more coins",
            "",
            "Good luck and have fun shopping",
             "at Tindahan ni Aling Nena!"
        ]
        
        # Render all text lines
        rendered_lines = []
        total_height = 0
        
        for line in how_to_play_text:
            if line:  # If line is not empty
                rendered_text = content_font.render(line, True, WHITE)
            else:  # Empty line for spacing
                rendered_text = content_font.render(" ", True, WHITE)
            
            rendered_lines.append(rendered_text)
            total_height += rendered_text.get_height() + 10  # 10px spacing between lines
        
        # Calculate maximum scroll value
        content_area['max_scroll'] = max(0, total_height - content_area['height'])
        
        # Main loop
        while how_to_play:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    how_to_play = False
                    self.running = False
                
                # Handle mouse wheel scrolling
                elif event.type == pygame.MOUSEWHEEL:
                    content_area['scroll_y'] -= event.y * content_area['scroll_speed']
                    # Clamp scroll value
                    content_area['scroll_y'] = max(0, min(content_area['max_scroll'], content_area['scroll_y']))
                
                # Handle key presses for scrolling
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        content_area['scroll_y'] -= content_area['scroll_speed']
                    elif event.key == pygame.K_DOWN:
                        content_area['scroll_y'] += content_area['scroll_speed']
                    
                    # Clamp scroll value
                    content_area['scroll_y'] = max(0, min(content_area['max_scroll'], content_area['scroll_y']))
            
            # Draw main background
            self.screen.blit(self.how_to_play_bg, (0, 0))
            
            # Draw title
            self.screen.blit(title_text, title_rect)
            
            # Draw the text background image
            self.screen.blit(text_bg_image, (text_bg_rect.x, text_bg_rect.y))
            
            # Create a clipping rect for the content area
            content_rect = pygame.Rect(
                content_area['x'], 
                content_area['y'], 
                content_area['width'], 
                content_area['height']
            )
            
            # Save the current clip area
            original_clip = self.screen.get_clip()
            
            # Set clip area to content area
            self.screen.set_clip(content_rect)
            
            # Draw content within the clipped area
            y_pos = content_area['y'] - content_area['scroll_y']
            
            for line in rendered_lines:
                if y_pos + line.get_height() > content_area['y'] and y_pos < content_area['y'] + content_area['height']:
                    # Left-align text with margin
                    margin_left = 20  # Adjust this value for desired left margin
                    line_x = content_area['x'] + margin_left
                    
                    self.screen.blit(line, (line_x, y_pos))
                y_pos += line.get_height() + 10
            
            # Reset clip area
            self.screen.set_clip(original_clip)
            
            # Draw scroll indicators if needed
            if content_area['scroll_y'] > 0:
                # Draw up arrow
                pygame.draw.polygon(self.screen, WHITE, [
                    (content_area['x'] + content_area['width'] - 20, content_area['y'] + 10),
                    (content_area['x'] + content_area['width'] - 10, content_area['y'] + 20),
                    (content_area['x'] + content_area['width'] - 30, content_area['y'] + 20)
                ])
            
            if content_area['scroll_y'] < content_area['max_scroll']:
                # Draw down arrow
                pygame.draw.polygon(self.screen, WHITE, [
                    (content_area['x'] + content_area['width'] - 20, content_area['y'] + content_area['height'] - 10),
                    (content_area['x'] + content_area['width'] - 10, content_area['y'] + content_area['height'] - 20),
                    (content_area['x'] + content_area['width'] - 30, content_area['y'] + content_area['height'] - 20)
                ])
            
            # Draw back button
            back_button.draw(self.screen)
            
            # Check if back button is pressed
            if back_button.is_pressed(pygame.mouse.get_pos(), pygame.mouse.get_pressed()):
                how_to_play = False
            
            self.clock.tick(FPS)
            pygame.display.update()

    def intro_screen(self):
        intro = True

        title = self.font.render('Tindahan', True, WHITE)
        title2 = self.font.render('ni Aling Nena', True, WHITE)
        self.title_rect = title.get_rect(x=275, y=25)
        self.title2_rect = title2.get_rect(x=200, y=55)
        title_bg = pygame.image.load('img\DBOX.png')
        title_bg = pygame.transform.scale(title_bg, (670, 150)) 
        button_image_path = 'c:\\Users\\This PC\\OneDrive\\Documents\\054\\TindahanGame\\img\\ABUT.png'
        
        play_button = Button(281, 120, 240, 50, button_image_path, WHITE, 'Play', self.font_button)
        options_button = Button(281, 180, 240, 50, button_image_path, WHITE, 'Options', self.font_button)
        exit_button = Button(750, 5, 50, 50, button_image_path, WHITE, 'X', self.font_button)
        credits_button = Button(281, 240, 240, 50, button_image_path, WHITE, 'Credits', self.font_button)
        how_to_play_button = Button(10, 5, 50, 50, button_image_path, WHITE, '?', self.font_button)
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
                self.run_game_loop()  # Start the game loop instead of calling self.main()
            
            if options_button.is_pressed(mouse_pos, mouse_pressed):
                self.options_screen()

            if exit_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
                self.running = False
                pygame.quit()
                sys.exit()
            
            if credits_button.is_pressed(mouse_pos, mouse_pressed):
                self.credits_screen()

            if how_to_play_button.is_pressed(mouse_pos, mouse_pressed):
                self.how_to_play_screen()

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title_bg, (70, -20))
            self.screen.blit(title, self.title_rect)  
            self.screen.blit(title2, self.title2_rect)  
            play_button.draw(self.screen)
            options_button.draw(self.screen)
            credits_button.draw(self.screen)
            how_to_play_button.draw(self.screen)
            exit_button.draw(self.screen)
            
            self.clock.tick(FPS)
            pygame.display.update()

g = Game()
g.intro_screen()
while g.running:
    g.run_game_loop()  # Run the game loop 3 times
    g.game_over()

pygame.quit()
sys.exit()
