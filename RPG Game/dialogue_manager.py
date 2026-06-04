import pygame

class DialogueManager:
    def __init__(self):
        self.box = pygame.image.load(r"RPG Game\sprites\dialogue_box.png")
        self.yes_no_box = pygame.image.load(r"RPG Game\sprites\dialogue_yes_no_box.png")
        self.arrow = pygame.image.load(r"RPG Game\sprites\dialogue_box_arrow.png")
        self.rotated_arrow = pygame.transform.rotate(self.arrow, 90)
        self.font_size = 16
        self.font = pygame.font.Font(r"C:\Users\hchok\Downloads\Press_Start_2P\PressStart2P-Regular.ttf", self.font_size)
        self.message = ""
        self.color = (34, 34, 34)
        self.text_surface = self.font.render(self.message, False, self.color)
        self.width = self.box.get_width()
        self.height = self.box.get_height()

        self.box_x = 0
        self.box_y = 0


        self.arrow_y = 0
        self.arrow_x = 0
        self.key_timer = 0
        self.base_arrow_y = self.arrow_y

        self.choice_index = 0
        self.line_height = self.font_size
        
        self.active = False
        self.speed = 60

    def init_arrow_pos(self):
        self.arrow_x = self.box_x + self.width - self.yes_no_box.get_width() + 18
        self.base_arrow_y = self.box_y - self.yes_no_box.get_height() + 14
        self.arrow_y = self.base_arrow_y

    def start_yes_no(self, surface):
        full_text = "Yes\nNo"
        lines = full_text.split("\n")

        surface.blit(self.yes_no_box, (self.box_x + self.width - self.yes_no_box.get_width(), self.box_y - self.yes_no_box.get_height() + 12))

        for index, line in enumerate(lines):
            text = self.font.render(line, False, self.color)
            surface.blit(text, (self.box_x + self.width - self.yes_no_box.get_width() + 40, (self.box_y - self.yes_no_box.get_height() + 32) + index * text.get_height()))

        
    
    def start_dialogue(self, message):
        self.message = message
        self.index = 0
        self.timer = 0
        self.active = True

    def update_dialogue(self, dt):
        if not self.active:
            return

        self.timer += dt

        # adjust speed here
        if self.timer >= self.speed:
            self.timer = 0

            if self.index < len(self.message):
                self.index += 1


    def get_text_surface(self, surface, x, y):
        visible_text = self.message[:self.index]
        lines = visible_text.split("\n")

        for index, line in enumerate(lines):
            text = self.font.render(line, False, self.color)
            surface.blit(text, (x, y + index * text.get_height()))

    def start_arrow(self):
        self.blink_timer = 0
        self.blink_interval = 200
        self.visible = True

    def update_arrow(self, dt):
        self.blink_timer += dt

        if self.blink_timer >= self.blink_interval:
            self.blink_timer = 0
            self.visible = not self.visible

    def draw_arrow(self, surface, x, y):
        if self.visible:
            surface.blit(self.arrow, (x, y))

    def stop_arrow(self):
        self.visible = False

    def move_arrow(self, surface, dt):
        keys = pygame.key.get_pressed()
        self.key_timer += dt

        line_height = self.font_size
        line_gap = 4

        if self.key_timer >= 200:
            if keys[pygame.K_UP]:
                self.key_timer = 0
                self.choice_index = max(0, self.choice_index - 1)

            if keys[pygame.K_DOWN]:
                self.key_timer = 0
                self.choice_index = min(1, self.choice_index + 1)

        self.arrow_y = self.base_arrow_y + self.choice_index * (line_height + line_gap) + 14
        surface.blit(self.rotated_arrow, (self.arrow_x, self.arrow_y))
                

    

        
