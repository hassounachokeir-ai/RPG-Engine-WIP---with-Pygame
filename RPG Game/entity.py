import pygame
import json
from settings import TILE_SIZE, SCALE

class Entity:
    def __init__(self, state, direction):
        self.state = state
        self.direction = direction
        self.sprites = []
        self.flipped_sprites = []
        self.data = None
        self.type = None
        self.id = 0
        self.visible = True

        self.world_x = 0
        self.world_y = 0
        self.draw_x = self.world_x
        self.draw_y = self.world_y
        self.velocity_x = 0
        self.velocity_y = 0

        self.hitbox = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        self.hitbox_width = 0
        self.hitbox_height = 0
        self.hitbox_x_offset = 0
        self.hitbox_y_offset = 0
        self.hitbox_x = 0
        self.hitbox_y = 0

        self.timer = 0

        self.start_frame = 0
        self.frame = 0
        self.frame_count = 0
        self.frame_delay = 0

        self.tile_width = 16
        self.tile_height = 32
        

    def load_data(self):
        with open(r"C:\Users\hchok\OneDrive\Desktop\Python Projects\RPG Game\metadata\entities_metadata.json", "r") as file:
            self.data = json.load(file)


    def subsurface_sheet(self, sheet):
        image = pygame.image.load(sheet).convert_alpha()
        sheet_width = image.get_width()
        sheet_height = image.get_height()

        for y in range(0, sheet_height, self.tile_height):
            for x in range(0, sheet_width, self.tile_width):
                rect = pygame.Rect(x, y, self.tile_width, self.tile_height)
                sprite = image.subsurface(rect)
                new_sprite = pygame.transform.scale(sprite, (self.tile_width * SCALE, self.tile_height * SCALE))

                self.sprites.append(new_sprite)

        for s in self.sprites:
            self.flipped_sprites.append(pygame.transform.flip(s, True, False))

    def set_hitbox(self):

        self.hitbox_y_offset = self.data[self.type][self.id]["hitbox"][1] * SCALE
        self.hitbox_width = self.data[self.type][self.id]["hitbox"][2] * SCALE
        self.hitbox_height = self.data[self.type][self.id]["hitbox"][3] * SCALE

        if self.direction == "right":
            self.hitbox_x_offset = self.data[self.type][self.id]["hitbox"][0] * SCALE
        elif self.direction == "left":
            self.hitbox_x_offset = self.sprites[0].get_width() - (self.data[self.type][self.id]["hitbox"][0] * SCALE + self.hitbox_width) 
                        
        self.hitbox_x = (self.draw_x + self.hitbox_x_offset)
        self.hitbox_y = (self.draw_y + self.hitbox_y_offset)
                    
        self.hitbox = pygame.Rect(self.hitbox_x, self.hitbox_y, self.hitbox_width, self.hitbox_height)


    def update_frame_data(self):
        self.frame_count = len(self.data[self.type][self.id]["animation_frames"][self.state])
        self.frame_delay = self.data[self.type][self.id]["animation_frames"]["delay"]
        self.start_frame = self.data[self.type][self.id]["animation_frames"][self.state][0]  

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.frame = 0
            self.timer = 0

            self.update_frame_data()

    def animate(self):
        if self.frame_count == 0:
            return

        if self.timer >= self.frame_delay:
            self.timer = 0
            self.frame = (self.frame + 1) % self.frame_count
        
    def update(self, dt):
        self.timer += dt
        self.animate()
        self.set_hitbox()
    
