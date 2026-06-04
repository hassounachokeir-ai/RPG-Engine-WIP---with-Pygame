import pygame
import json
import random

from entity import Entity
from settings import TILE_SIZE

class NPC(Entity):
    def __init__(self, x, y, state, direction, npc_id, referral_code=None):
        
        self.npc_id = npc_id
        self.solid = False
                
        super().__init__(state, direction)
        super().load_data()
        super().subsurface_sheet(self.data["npcs"][self.npc_id]["image"])

        self.world_x = x
        self.world_y = y

        self.draw_x = x
        self.draw_y = y - self.sprites[0].get_height() + TILE_SIZE

        self.destination_x = self.world_x
        self.destination_y = self.world_y
        self.move_x = 0
        self.move_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.target_offset_x = 0
        self.target_offset_y = 0
        
        self.type = "npcs"
        self.id = self.npc_id

        self.update_frame_data()
        
        if referral_code is None:
            self.referral_code = self.generate_id()
        else:
            self.referral_code = referral_code
            
        self.event_state = 0
        self.event = {}
        self.saved_event_state = None

        self.active_event = None
        self.moving = False
        self.going_to_player = False
        self.following_player = False
        self.moving_to_player = False
        self.event_running = False
        self.speaking = False
        self.event_just_reset = False
        self.direction_x = "none"
        self.direction_y = "none"

        self.load_npc_data()
        self.read_npc_data()
    
    def generate_id(self):
        return "npc_" + str(random.randint(1_000_000, 9_999_999))

    def load_npc_data(self):
        with open(r"C:\Users\hchok\OneDrive\Desktop\Python Projects\RPG Game\metadata\npc_metadata.json", "r") as file:
            self.npc_data = json.load(file)

    def read_npc_data(self):
        if self.npc_data is None:
            self.npc_data = {}

        if self.referral_code not in self.npc_data:
            self.event = {}
            return

        self.solid = self.npc_data.get(self.referral_code).get("solid")

    def update_event(self, global_event_state):
        if self.referral_code in self.npc_data:
            branch = self.npc_data[self.referral_code]["event_state"].get(str(global_event_state), {})
            self.event = branch.get(str(self.event_state), {})

            if not self.event:
                self.event = self.npc_data[self.referral_code]["event_state"].get("all", {}).get(str(self.event_state), {})

            self.saved_event_state = self.npc_data[self.referral_code]["event_state"]
        

    def set_npc_id(self, npc_id):
        self.npc_id = npc_id
        self.id = npc_id

        self.sprites.clear()
        self.flipped_sprites.clear()

        self.subsurface_sheet(self.data["npcs"][self.npc_id]["image"])
        self.update_frame_data()

    def update_coords(self):
        self.draw_x = self.world_x
        self.draw_y = self.world_y - self.sprites[0].get_height() + TILE_SIZE

    def start_movement(self, x, y):
        self.moving = True
        self.destination_x = self.world_x + x 
        self.destination_y = self.world_y + y

        self.move_x = 1 if x > 0 else -1 if x < 0 else 0
        self.move_y = 1 if y > 0 else -1 if y < 0 else 0
    
    def update_movement(self):
        if not self.world_x == self.destination_x:
            self.world_x += self.move_x
            self.direction_x = "right" if self.move_x > 0 else "left" if self.move_x < 0 else 0
            self.direction = "right" if self.move_x > 0 else "left" if self.move_x < 0 else self.direction
        else:
            self.direction_x = "none"
            
        if not self.world_y == self.destination_y:
            self.world_y += self.move_y
            self.direction_y = "down" if self.move_y > 0 else "up" if self.move_y < 0 else 0
        else:
            self.direction_y = "none"

        if self.world_x == self.destination_x and self.world_y == self.destination_y:
            self.direction_x = "none"
            self.direction_y = "none"
            self.moving = False


    def start_follow(self, x, y):
        self.going_to_player = True
        self.destination_x = int(x)
        self.destination_y = int(y)

        self.move_x = 1 if x > self.world_x else -1 if x < self.world_x else 0
        self.move_y = 1 if y > self.world_y else -1 if y < self.world_y else 0

    def follow_player(self): 
        if self.world_x != self.destination_x:
            self.world_x += self.move_x
            self.direction = "right" if self.move_x > 0 else "left" if self.move_x < 0 else self.direction
            
        if self.world_y != self.destination_y:
            self.world_y += self.move_y

        if self.world_x == self.destination_x and self.world_y == self.destination_y:
            self.going_to_player = False
            self.following_player = True

    def update_offsets(self, direction):
        if direction == "right":
            self.target_offset_x = -32
            self.target_offset_y = 32

        elif direction == "left":
            self.target_offset_x = 32
            self.target_offset_y = 32

    def smooth_offsets(self):
        speed = 2

        if self.offset_x < self.target_offset_x:
            self.offset_x += speed
        elif self.offset_x > self.target_offset_x:
            self.offset_x -= speed

        if self.offset_y < self.target_offset_y:
            self.offset_y += speed
        elif self.offset_y > self.target_offset_y:
            self.offset_y -= speed
            

    def set_state(self, velocity_x, velocity_y):
        if self.moving or self.going_to_player:
            super().set_state("run")
            
        elif self.following_player:
            
            if velocity_x != 0 or velocity_y != 0:
                super().set_state("run")
            else:
                super().set_state("idle")
                
        else:
            super().set_state("idle")


    def update(self, dt, global_event_state, vx, vy):
        self.update_coords()
        super().update(dt)
        self.set_state(vx, vy)
        self.update_event(global_event_state)
        

    
        
    
