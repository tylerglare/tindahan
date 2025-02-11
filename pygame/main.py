import pygame
from sprites import *
from config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('arial.ttf', 32)
        self.running = True
        
        self.character_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/JUNJUN IDLE RIGHT.png')
        self.mainwalkright_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/JUNJUN WALK RIGHT.png')
        self.mainwalkleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/JUNJUN WALK LEFT.png')
        self.terrain_spritesheet = Spritesheet('img/house.png')
        self.enemywalkright_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/TAMBAY1 WALK RIGHT.png')
        self.enemywalkleft_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/TAMBAY1 WALK LEFT.png')
        self.enemyidle_spritesheet = Spritesheet('img/TINDAHAN CHARACTERS/TAMBAY1 IDLE RIGHT.png')
        self.intro_background = pygame.image.load('img/INTROSTORE.jpg')
        self.intro_background = pygame.transform.scale(self.intro_background, (800, 512))
        self.go_background = pygame.image.load('img/gameover.png')

    def createTilemap(self):
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                Ground(self, j, i)
                if column == 'B':
                    Block(self, j, i)
                if column == "E":
                    Enemy(self, j, i)
                if column == 'P':
                    self.player = Player(self, j, i)

    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.createTilemap()

    def show_question(self, question, choices):
        question_box = pygame.Rect(WIN_WIDTH // 4, WIN_HEIGHT // 4, WIN_WIDTH // 2, 100)
        font = pygame.font.Font(None, 24)
        text = font.render(question, True, WHITE)
        text_rect = text.get_rect(center=question_box.center)
        
        buttons = []
        button_width = 200
        button_height = 40
        button_x = WIN_WIDTH // 3
        button_y = WIN_HEIGHT // 2
        
        for i, choice in enumerate(choices):
            button_rect = pygame.Rect(button_x, button_y + i * (button_height + 10), button_width, button_height)
            buttons.append((button_rect, choice))

        running = True
        while running:
            self.screen.fill(BLACK, question_box)
            pygame.draw.rect(self.screen, WHITE, question_box, 2)
            self.screen.blit(text, text_rect)
            
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
                    for button, choice in buttons:
                        if button.collidepoint(event.pos):
                            print(f"Player chose: {choice}")
                            running = False
            
            pygame.time.delay(100)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
    
    def update(self):
        self.all_sprites.update()
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if enemy_hits:
            self.show_question("Anong ambag mo?", ["1", "2", "3", "4"])
    
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)
        pygame.display.update()
    
    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
    
    def intro_screen(self):
        intro = True
        play_button = Button(10, 50, 100, 50, WHITE, BLACK, 'Play', 32)
        
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
            
            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()

pygame.quit()
sys.exit()
