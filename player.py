import pygame
import json
from entity import Entity
from settings import SCALE, TILE_SIZE

class Player(Entity):
    def __init__(self, state, direction):
        super().__init__(state, direction)
        self.read_data()

        self.type = "player"
        self.id = 0
        
        super().load_data()
        super().subsurface_sheet(self.data["player"][0]["image"])

        self.speed = 1
        self.editor = None
    
        super().update_frame_data()

        self.moving = False
        self.following = False
        self.can_move = True
        self.player_flag = True
        
        self.destination_x = 0
        self.destination_y = 0
        self.move_x = 0
        self.move_y = 0
        self.direction_x = "none"
        self.direction_y = "none"

        self.event_running = False

        self.offset_x = 0
        self.offset_y = 0
        self.target_offset_x = 0
        self.target_offset_y = 0

    def read_data(self):
        with open(r"C:\Users\hchok\OneDrive\Desktop\Python Projects\RPG Game\metadata\saved_data.json", "r") as file:
            d = json.load(file)

        p = d.get("player", {})

        self.world_x = p.get("world_x", 0)
        self.world_y = p.get("world_y", 0)
        self.state = p.get("state", "idle")
        self.direction = p.get("direction", "right")

    def set_speed(self):
        if self.editor:
            self.speed = 2
        if not self.editor:
            self.speed = 0.5
        
    def key_pressed(self):
        keys = pygame.key.get_pressed()
        
        if self.can_move:
            if keys[pygame.K_d]:
                self.direction = "right"
                self.velocity_x += self.speed
               
            if keys[pygame.K_a]:
                self.direction = "left"
                self.velocity_x -= self.speed
                
            if keys[pygame.K_w]:
                self.velocity_y -= self.speed
                
            if keys[pygame.K_s]:
                self.velocity_y += self.speed

            self.velocity_x *= 0.9
            self.velocity_y *= 0.9

            if self.velocity_x < 0.1 and self.velocity_x > -0.1:
                self.velocity_x = 0
            if self.velocity_y < 0.1 and self.velocity_y > -0.1:
                self.velocity_y = 0
        else:
            self.velocity_x = 0
            self.velocity_y = 0


    def set_state(self):
        if self.can_move:
            if self.velocity_x != 0 or self.velocity_y != 0:
                super().set_state("run")
                self.direction_x = "right" if self.velocity_x > 0 else "left" if self.velocity_x < 0 else "none"
                self.direction_y = "down" if self.velocity_y > 0 else "up" if self.velocity_y < 0 else "none"
            else:
                super().set_state("idle")
        else:
            if self.moving:
                super().set_state("run")
            else:
                if self.following:
                    super().set_state("run")
                else:
                    super().set_state("idle")

    def moving_horizontally(self, hitbox_list, entity_list):
        self.world_x += self.velocity_x
        self.draw_x = self.world_x
        self.draw_y = self.world_y
        self.set_hitbox()

        if not self.editor:

            for hitbox in hitbox_list:
                if self.hitbox.colliderect(hitbox):

                    if self.velocity_x > 0: #moving right
                        self.world_x = (
                            hitbox.left
                            - self.hitbox.width
                            - self.hitbox_x_offset
                        )
                    elif self.velocity_x < 0: #moving left
                        self.world_x = (
                            hitbox.right
                            - self.hitbox_x_offset
                        )
                        
                    self.velocity_x = 0
                    self.draw_x = self.world_x
                    self.draw_y = self.world_y
                    self.set_hitbox()
                    break

                for entity in entity_list:
                    if self.hitbox.colliderect(entity.hitbox) and entity.solid:

                        if self.velocity_x > 0: #moving right
                            self.world_x = (
                                entity.hitbox.left
                                - self.hitbox.width
                                - self.hitbox_x_offset
                            )
                        elif self.velocity_x < 0: #moving left
                            self.world_x = (
                                entity.hitbox.right
                                - self.hitbox_x_offset
                            )
                            
                        self.velocity_x = 0
                        self.draw_x = self.world_x
                        self.draw_y = self.world_y
                        self.set_hitbox()
                        break


    def moving_vertically(self, hitbox_list, entity_list):
        self.world_y += self.velocity_y
        self.draw_x = self.world_x
        self.draw_y = self.world_y
        self.set_hitbox()

        if not self.editor:

            for hitbox in hitbox_list:
                if self.hitbox.colliderect(hitbox):

                    if self.velocity_y > 0: #moving down
                        self.world_y = (
                            hitbox.top
                            - self.hitbox.height
                            - self.hitbox_y_offset
                        )
                    elif self.velocity_y < 0: #moving up
                        self.world_y = (
                            hitbox.bottom
                            - self.hitbox_y_offset
                        )

                    self.velocity_y = 0
                    self.draw_x = self.world_x
                    self.draw_y = self.world_y
                    self.set_hitbox()
                    break
                
            for entity in entity_list:
                if self.hitbox.colliderect(entity.hitbox) and entity.solid:

                    if self.velocity_y > 0: #moving down
                        self.world_y = (
                            entity.hitbox.top
                            - self.hitbox.height
                            - self.hitbox_y_offset
                        )
                    elif self.velocity_y < 0: #moving up
                        self.world_y = (
                            entity.hitbox.bottom
                            - self.hitbox_y_offset
                        )

                    self.velocity_y = 0
                    self.draw_x = self.world_x
                    self.draw_y = self.world_y
                    self.set_hitbox()
                    break
                

    def start_follow(self, x, y):
        self.moving = True
        self.destination_x = int(x)
        self.destination_y = int(y)

        self.move_x = 1 if x > self.world_x else -1 if x < self.world_x else 0
        self.move_y = 1 if y > self.world_y else -1 if y < self.world_y else 0

        self.world_x = int(self.world_x)
        self.world_y = int(self.world_y)
        

    def follow_npc(self, entity_x): 
        
        if self.world_x != self.destination_x:
            self.world_x += self.move_x
            self.direction = "right" if self.move_x > 0 else "left" if self.move_x < 0 else self.direction
            
        if self.world_y != self.destination_y:
            self.world_y += self.move_y

        if self.world_x == self.destination_x and self.world_y == self.destination_y:
            if entity_x > self.world_x:
                self.direction = "right"
            else:
                self.direction = "left"

            self.moving = False
            

    def update_offsets(self, direction_x, direction_y):
        self.target_offset_x = -32 if direction_x == "right" else 32 if direction_x == "left" else 0
        self.target_offset_y = 32 if direction_y == "up" else -32 if direction_y == "down" else 0

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

    def update(self, dt):
        self.set_speed()
        self.key_pressed()
        self.set_state()
        super().update(dt)
        
