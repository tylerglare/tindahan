import pygame
import sys
import random
import json

class DialogueBox:
    def __init__(self, screen, player, npc, box_image_path, frame_image_path, width, height):
        self.screen = screen
        self.player = player
        self.image = pygame.image.load("img\DBOX.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.image_rect = self.image.get_rect()
        

        # Load portrait and frame
        if npc and npc.portrait_path:
            self.portrait = pygame.image.load(npc.portrait_path).convert_alpha()
            self.portrait = pygame.transform.scale(self.portrait, (128, 128))
        else:
            self.portrait = None

        self.frame = pygame.image.load("img/PROFILE1.png").convert_alpha()
        self.frame = pygame.transform.scale(self.frame, (170, 170))

        self.npc_name = npc.name if npc else "Unknown"
        self.width = width
        self.height = height

        # Font
        self.font = pygame.font.Font('PressStart2P-Regular.ttf', 15)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

    def fit_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw_dialogue_box(self, npc, text, current_text):
        box_x = 150
        box_y = 250
        frame_x = 50
        frame_y = 300

        # Draw dialogue box
        self.screen.blit(self.image, (box_x, box_y))
        self.screen.blit(self.frame, (frame_x, frame_y))

        # Draw portrait if available
        if self.portrait:
            portrait_x = frame_x + (self.frame.get_width() - self.portrait.get_width()) // 2
            portrait_y = frame_y + (self.frame.get_height() - self.portrait.get_height()) // 2 - 10
            self.screen.blit(self.portrait, (portrait_x, portrait_y))

        # Draw NPC name
        name_surface = self.font.render(self.npc_name, True, self.BLACK)
        name_rect = name_surface.get_rect(center=(frame_x + self.frame.get_width() // 2, frame_y + self.frame.get_height() - 25))
        self.screen.blit(name_surface, name_rect)

        # Draw text
        start_x = box_x + 140
        start_y = box_y + 80
        for i, line in enumerate(current_text.split("\n")):
            text_surface = self.font.render(line, True, self.WHITE)
            self.screen.blit(text_surface, (start_x, start_y + i * 20))

    def show_dialogue(self, npc, dialogue, question, choices, correct_answer, responses):
        button_x = 625
        button_y = 395

        self.next_button_image = pygame.image.load('img/ABUT.png').convert_alpha()
        self.next_button_image = pygame.transform.scale(self.next_button_image, (100, 30))

        next_button_rect = pygame.Rect(button_x, button_y, 100, 30)
        next_button_text = self.font.render("Next", True, self.WHITE)
        next_button_text_rect = next_button_text.get_rect(center=next_button_rect.center)

        running = True
        current_text = ""
        typing_speed = 50
        last_update = pygame.time.get_ticks()
        char_index = 0
        line_index = 0
        finished_typing = False

        # Split the dialogue into lines that fit the box width
        lines = self.fit_text(dialogue, 460)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if next_button_rect.collidepoint(event.pos):
                        if finished_typing:

                            running = False
                            self.player.game.draw()
                            pygame.display.flip()

                            # 👉 Transition to question box
                            question_box = QuestionBox(self.screen, self.player, self, 'img/QBOX.png', self.width, self.height)
                            question_box.show_question(npc, question, choices, correct_answer, responses)
                        else:
                            current_text = "\n".join(lines)
                            finished_typing = True

            # ✅ Use the draw_dialogue_box function
            self.draw_dialogue_box(npc, dialogue, current_text)

            # Typing effect
            if not finished_typing:
                if char_index < len(lines[line_index]):
                    if pygame.time.get_ticks() - last_update > typing_speed:
                        current_text += lines[line_index][char_index]
                        char_index += 1
                        last_update = pygame.time.get_ticks()
                else:
                    if line_index < len(lines) - 1:
                        line_index += 1
                        char_index = 0
                        current_text += "\n"
                    else:
                        finished_typing = True

            # Draw Next button
            self.screen.blit(self.next_button_image, next_button_rect.topleft)
            self.screen.blit(next_button_text, next_button_text_rect)

            pygame.display.flip()

    def show_response(self, npc, response):

        if not response:
            response = "No response available."  # Default message

        lines = self.fit_text(response, 460)
        button_x = 625
        button_y = 395

        self.next_button_image = pygame.image.load('img/ABUT.png').convert_alpha()
        self.next_button_image = pygame.transform.scale(self.next_button_image, (100, 30))

        next_button_rect = pygame.Rect(button_x, button_y, 100, 30)
        next_button_text = self.font.render("Back", True, self.WHITE)
        next_button_text_rect = next_button_text.get_rect(center=next_button_rect.center)

        running = True
        current_text = ""
        typing_speed = 50
        last_update = pygame.time.get_ticks()
        char_index = 0
        line_index = 0
        finished_typing = False

        # Split the response into lines that fit the box width
        lines = self.fit_text(response, 460)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if next_button_rect.collidepoint(event.pos):
                        if finished_typing:
                            running = False  # Back to game
                        else:
                            current_text = "\n".join(lines)
                            finished_typing = True

            # ✅ Use the draw_dialogue_box function
            self.draw_dialogue_box(npc, response, current_text)

            # Typing effect
            if not finished_typing:
                if char_index < len(lines[line_index]):
                    if pygame.time.get_ticks() - last_update > typing_speed:
                        current_text += lines[line_index][char_index]
                        char_index += 1
                        last_update = pygame.time.get_ticks()
                else:
                    if line_index < len(lines) - 1:
                        line_index += 1
                        char_index = 0
                        current_text += "\n"
                    else:
                        finished_typing = True

            # Draw Back button
            self.screen.blit(self.next_button_image, next_button_rect.topleft)
            self.screen.blit(next_button_text, next_button_text_rect)

            pygame.display.flip()



class QuestionBox:
    def __init__(self, screen, player, dialogue_box, box_image_path, width, height):
        self.screen = screen
        self.player = player
        self.dialogue_box = dialogue_box
        self.image = pygame.image.load("img/DBOX.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))

        self.width = width
        self.height = height

        self.font = pygame.font.Font('PressStart2P-Regular.ttf', 15)
        self.WHITE = (255, 255, 255)

        self.button_image = pygame.image.load('img/ABUT.png').convert_alpha()
        self.button_width = 300
        self.button_height = 80
        self.button_image = pygame.transform.scale(self.button_image, (self.button_width, self.button_height))



    def adjust_brightness(self, button_image, factor):
        """Adjust the brightness of the button image."""
        img = button_image.copy()

        # Iterate through every pixel in the image and adjust brightness
        width, height = img.get_size()

        for x in range(width):
            for y in range(height):
                color = img.get_at((x, y))  # Get the color at (x, y) as a pygame.Color
                r, g, b, a = color  # Extract the red, green, blue, and alpha components

                # Apply the factor and make sure the values stay within 0-255
                r = min(int(r * factor), 255)
                g = min(int(g * factor), 255)
                b = min(int(b * factor), 255)

                # Set the new color back to the pixel
                img.set_at((x, y), (r, g, b, a))

        return img


    def fit_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def show_question(self, npc, question, choices, correct_answer, responses):
        question_box = pygame.Rect(50, 100, 300, 100)
        buttons = []

        button_x = 150
        button_y = 320
        button_spacing_x = 350
        button_spacing_y = 100
        lines = self.fit_text(question, 460)
        for i, choice in enumerate(choices):
            col = i % 2
            row = i // 2
            x = button_x + col * button_spacing_x
            y = button_y + row * button_spacing_y

            button_rect = pygame.Rect(x, y, self.button_width, self.button_height)
            buttons.append((button_rect, choice))

        running = True
        while running:
            self.screen.blit(self.image, (question_box.x, question_box.y))

            question_text = self.font.render(question, True, self.WHITE)
            text_rect = question_text.get_rect()
            text_rect.x = 200  # Set X position
            text_rect.y = 170  # Set Y position
            self.screen.blit(question_text, text_rect)

            for button, choice in buttons:
                self.screen.blit(self.button_image, button.topleft)
                choice_text = self.font.render(choice, True, self.WHITE)
                self.screen.blit(choice_text, choice_text.get_rect(center=button.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button, choice in buttons:
                        mouse_pos = pygame.mouse.get_pos()

                        # Adjust brightness for hover
                        if button.collidepoint(mouse_pos):
                            button_image = self.adjust_brightness(self.button_image, 5)  # Brighter on hover
                        else:
                            button_image = self.button_image

                        self.screen.blit(button_image, button.topleft)

                        # Handle click
                        if event.type == pygame.MOUSEBUTTONDOWN and button.collidepoint(event.pos):
                            running = False
                            self.player.game.draw()
                            pygame.display.flip()
                            
                            # Handle answer result
                            if choice == correct_answer:
                                self.player.coins += 1
                                response = random.choice(responses["correct"])  # Pick a correct response
                                if npc and hasattr(npc, 'return_to_spawn'):
                                    npc.return_to_spawn()
                            else:
                                self.player.coins -= 1
                                response = random.choice(responses["wrong"])  # Pick a wrong response

                            print(f"Coins: {self.player.coins}")
                            
                            # Pass the selected string response instead of the whole dictionary
                            response_box = DialogueBox(self.screen, self.player, npc, 'img/QBOX.png', 'img/frame.png', self.width, self.height)
                            response_box.show_response(npc, response)  # Pass a single string response

            pygame.time.delay(100)
