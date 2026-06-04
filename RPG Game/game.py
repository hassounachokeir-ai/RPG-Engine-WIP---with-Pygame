import pygame
from tile_editor import TileEditor
from player import Player
from data_saver import DataSaver
from settings import TILE_SIZE
from dialogue_manager import DialogueManager


class Game:
    def __init__(self, width, height, caption):
        self.width = width
        self.height = height
        self.caption = pygame.display.set_caption(caption)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.running = True
        self.keys = pygame.key.get_pressed()

        self.hitbox_mode = True
        
        self.player = Player("idle", "right")
        self.start_x = self.width // 2 - self.player.sprites[0].get_width()
        self.start_y = self.height // 2 - self.player.sprites[0].get_height()

        self.player.world_x = self.start_x
        self.player.world_y = self.start_y

        self.player.read_data()

        self.tile_editor = TileEditor(self.player)
        self.tile_surfaces = self.tile_editor.get_tile_surfaces()

        self.player.editor = self.tile_editor.editor

        self.data_saver = DataSaver(self.tile_editor, self.player)

        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(60)
        self.timer = 0
        
        self.event_timer = 0
        self.waiting = False
        self.delay = 0

        self.fade_surface_alpha = 255
        self.fading = False
        self.fade_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.dialogue_manager = DialogueManager()
        self.global_event_state = 0
        self.dialogue_entity = None
        self.following_entity = None
        self.pending_move = None

        self.yes_no = False
        

    def tick(self):
        self.dt = self.clock.tick(60)
        self.timer += self.dt
        self.event_timer += self.dt
        self.player.editor = self.tile_editor.editor
        self.keys = pygame.key.get_pressed()

    def draw_tiles(self):

        for i in range(2):
            for tile in self.tile_editor.tiles:
                if tile.layer == i:
                    self.screen.blit(self.tile_surfaces[tile.tile_id], (tile.x_pos - self.tile_editor.camera_x, tile.y_pos - self.tile_editor.camera_y))

            if i == self.tile_editor.layer:
                for tile in self.tile_editor.tiles:
                    if tile.layer == i:
                        self.screen.blit(self.tile_editor.overlay, (tile.x_pos - self.tile_editor.camera_x, tile.y_pos - self.tile_editor.camera_y))
                        
        if self.hitbox_mode:
            for hitbox in self.tile_editor.hitboxes:
                pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(hitbox.x - self.tile_editor.camera_x, hitbox.y - self.tile_editor.camera_y, hitbox.width, hitbox.height), 1)

    def draw_third_layer(self):

            for tile in self.tile_editor.tiles:
                if tile.layer == 2:
                    self.screen.blit(self.tile_surfaces[tile.tile_id], (tile.x_pos - self.tile_editor.camera_x, tile.y_pos - self.tile_editor.camera_y))

                if self.tile_editor.layer == 2:
                        if tile.layer == 2:
                            self.screen.blit(self.tile_editor.overlay, (tile.x_pos - self.tile_editor.camera_x, tile.y_pos - self.tile_editor.camera_y))

            if self.hitbox_mode:
                for hitbox in self.tile_editor.hitboxes:
                    pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(hitbox.x - self.tile_editor.camera_x, hitbox.y - self.tile_editor.camera_y, hitbox.width, hitbox.height), 1)

       
    def draw_cursor(self):
        if self.tile_editor.tileset_library == "tiles":
            self.screen.blit(
                self.tile_surfaces[self.tile_editor.cursor.tile_id],
                (self.tile_editor.cursor_x - self.tile_editor.camera_x,
                 self.tile_editor.cursor_y - self.tile_editor.camera_y)
            )

            
        elif self.tile_editor.tileset_library == "npcs":
            self.screen.blit(
                self.tile_editor.cursor.sprites[0],
                (self.tile_editor.cursor_x - self.tile_editor.camera_x,
                 self.tile_editor.cursor_y - self.tile_editor.camera_y)
            )

        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            pygame.Rect(
                self.tile_editor.cursor_x - self.tile_editor.camera_x,
                self.tile_editor.cursor_y - self.tile_editor.camera_y,
                TILE_SIZE,
                TILE_SIZE),
                1
            )


    def draw_player(self):
        pos = (
            self.player.world_x - self.tile_editor.camera_x,
            self.player.world_y - self.tile_editor.camera_y
        )

        sprite_index = self.player.start_frame + self.player.frame

        if self.player.direction == "right":
            sprite = self.player.sprites[sprite_index]
            self.screen.blit(sprite, pos)
        else:
            sprite = self.player.flipped_sprites[sprite_index]
            self.screen.blit(sprite, pos)
            
        if self.hitbox_mode:
            pygame.draw.rect(self.screen,
                             (255, 0, 0),
                             pygame.Rect(self.player.hitbox.x - self.tile_editor.camera_x, self.player.hitbox.y - self.tile_editor.camera_y,
                                         self.player.hitbox.width, self.player.hitbox.height),
                             1)

    def draw_entity(self, entity):
            entity.update(self.dt, self.global_event_state, self.player.velocity_x, self.player.velocity_y)

            if not entity.visible:
                return
        
            pos = (
                entity.draw_x - self.tile_editor.camera_x,
                entity.draw_y - self.tile_editor.camera_y
            )
            sprite_index = entity.start_frame + entity.frame

            if entity.direction == "right":
                sprite = entity.sprites[sprite_index]
                self.screen.blit(sprite, pos)
            else:
                sprite = entity.flipped_sprites[sprite_index]
                self.screen.blit(sprite, pos)

            if self.hitbox_mode:
                pygame.draw.rect(self.screen, (255, 0, 0),
                                 pygame.Rect(entity.hitbox.x - self.tile_editor.camera_x, entity.hitbox.y - self.tile_editor.camera_y, entity.hitbox.width, entity.hitbox.height),
                                 1)
    

    def collide_player(self):
        self.player.moving_horizontally(self.tile_editor.hitboxes, self.tile_editor.entities)
        self.player.moving_vertically(self.tile_editor.hitboxes, self.tile_editor.entities)

    def key_pressed(self):
        if self.timer >= 200:
        
            if self.keys[pygame.K_m]:
                self.timer = 0
                print("Saved Successfully!")
                self.data_saver.save_data()

            if self.keys[pygame.K_h]:
                self.timer = 0
                self.hitbox_mode = not self.hitbox_mode

    def draw_entities(self):
        for entity in self.tile_editor.entities:
            if entity.hitbox.bottom < self.player.hitbox.bottom:
                self.draw_entity(entity)

        if self.player.visible:
            self.draw_player()

        for entity in self.tile_editor.entities:
            if entity.hitbox.bottom >= self.player.hitbox.bottom:
                self.draw_entity(entity)

    #=================================================
    # NPC Event Handling
    #=================================================

    def apply_global_event_change(self, new_state):
        self.global_event_state = new_state

        self.player.following = False
        self.player.moving = False
        self.player.event_running = False
        self.player.velocity_x = 0
        self.player.velocity_y = 0

        self.waiting = False
        self.fading = False

        for entity in self.tile_editor.entities:
            entity.moving = False
            entity.following_player = False
            entity.going_to_player = False
            entity.moving_to_player = False
            entity.event_running = False
            entity.speaking = False
            entity.event_just_reset = True
                

    def entity_events(self, entity):
        event = entity.event if isinstance(entity.event, dict) else {}
        entity.active_event = event.copy()
        
        self.player.can_move = False
        self.player.following = False
        self.player.moving = False
        self.player.velocity_x = 0
        self.player.velocity_y = 0

        if self.player.direction == "right":
            entity.direction = "left"
        elif self.player.direction == "left":
            entity.direction = "right"
        
        #event types
        if "dialogue" in event:
            entity.speaking = True
            self.dialogue_manager.start_dialogue(event.get("dialogue"))
            self.dialogue_manager.start_arrow()

        if "yes_no" in event:
            entity.speaking = True
            self.yes_no = True
            self.dialogue_manager.init_arrow_pos()
            self.dialogue_manager.start_dialogue(event.get("yes_no").get("text"))

        if "move" in event:
            move = event.get("move")
            if move:
                entity.start_movement(move[0] * TILE_SIZE, move[1] * TILE_SIZE)

        if "follow_npc" in event:
            self.player.event_running = True
            self.following_entity = entity
            follow_npc = event.get("follow_npc")

            if follow_npc:
                self.target_offset_x  = -TILE_SIZE if follow_npc[0] > 0 else TILE_SIZE if follow_npc[0] < 0 else 0
                self.target_offset_y = -TILE_SIZE if follow_npc[1] > 0 else TILE_SIZE if follow_npc[1] < 0 else 0

                self.player.start_follow(entity.world_x + self.player.offset_x, entity.world_y - TILE_SIZE + self.player.offset_y)

                self.pending_move = (entity, follow_npc[0]  * TILE_SIZE, follow_npc[1]  * TILE_SIZE)

        if "move_to_player" in event:
            entity.moving_to_player = True
            offset_x = TILE_SIZE if self.player.direction == "right" else -TILE_SIZE
            entity.start_movement(round((self.player.world_x - entity.world_x) / TILE_SIZE) * TILE_SIZE + offset_x,
                                  round((self.player.world_y + TILE_SIZE - entity.world_y) / TILE_SIZE) * TILE_SIZE)

        if "follow_player" in event:
            entity.start_follow(self.player.world_x, self.player.world_y)

        if "move_to_npc" in event:
            offset_x = TILE_SIZE if entity.direction == "right" else -TILE_SIZE
            self.player.start_follow(entity.world_x + offset_x, entity.world_y - TILE_SIZE)

        if "visibility" in event:
            entity.visible = event.get("visibility")

        if "player_visibility" in event:
            self.player.visible = event.get("player_visibility")

        if "wait" in event:
            self.waiting = True
            self.event_timer = 0
            self.delay = event.get("wait")

        if "fade" in event:
            self.fading = True
            self.fade_type = event.get("fade").get("type")
            self.fade_duration = event.get("fade").get("duration")

            if self.fade_type == "in":
                self.fade_surface_alpha = 0
            if self.fade_type == "out":
                self.fade_surface_alpha = 255

        if "pan_camera" in event:
            pan_camera = event.get("pan_camera")
            self.tile_editor.target_offset_x = pan_camera[0] * TILE_SIZE
            self.tile_editor.target_offset_y = pan_camera[1] * TILE_SIZE
            
        if "global_event" in event:
            new_state = event.get("global_event")
            self.apply_global_event_change(new_state)

    def yes_no_event_state(self, entity, event):
        yes_no = event.get("yes_no")
        if self.yes_no:
            entity.event_state = yes_no.get("yes_event") if self.dialogue_manager.choice_index == 0 else yes_no.get("no_event")
        else:
            entity.event_state = int(event.get("next_event"))


    def condition_types(self, entity, event=None):
        event = event or (entity.event if isinstance(entity.event, dict) else {})

        condition = event.get("condition")

        if condition == "player_has_gold":
            if self.player.player_flag:
                self.yes_no_event_state(entity, event)

        elif condition == "none":
           self.yes_no_event_state(entity, event)


    def handle_entity_events(self):
        for entity in self.tile_editor.entities:
            if entity.referral_code in entity.npc_data:

                #check trigger type, then event type, then trigger event
                event = entity.event if isinstance(entity.event, dict) else {}
                trigger  = event.get("trigger")

                if getattr(entity, 'event_just_reset', False) and not entity.event_running:
                    entity.event_just_reset = False
                    continue

                if not entity.visible and trigger in ("interact", "see_player"):
                    continue
                
                if trigger == "interact":
                    
                    distance = abs(self.player.hitbox.x - entity.hitbox.x) + abs(self.player.hitbox.y - entity.hitbox.y)
                    if distance < TILE_SIZE:
                        if self.keys[pygame.K_x] and not self.dialogue_manager.active:
                        
                            if not entity.event_running:
                                entity.event_running = True
                                self.entity_events(entity)
                            
                elif trigger == "see_player" and not self.dialogue_manager.active:
                    if abs(entity.hitbox.y - self.player.hitbox.y) < TILE_SIZE and abs(entity.hitbox.x - self.player.hitbox.x) < event["distance"] * TILE_SIZE:

                        if not entity.event_running:
                            entity.event_running = True
                            self.entity_events(entity)

                elif trigger == "automatic" and not self.dialogue_manager.active:
                    
                        if not entity.event_running:
                            entity.event_running = True
                            self.entity_events(entity)

    def set_camera_pos(self):
        self.tile_editor.camera_x = self.player.world_x - self.start_x + self.tile_editor.offset_x
        self.tile_editor.camera_y = self.player.world_y - self.start_y + self.tile_editor.offset_y

    def smooth_camera_offsets(self):
        speed = 2

        if self.tile_editor.offset_x < self.tile_editor.target_offset_x:
            self.tile_editor.offset_x += speed
        elif self.tile_editor.offset_x > self.tile_editor.target_offset_x:
            self.tile_editor.offset_x -= speed

        if self.tile_editor.offset_y < self.tile_editor.target_offset_y:
            self.tile_editor.offset_y += speed
        elif self.tile_editor.offset_y > self.tile_editor.target_offset_y:
            self.tile_editor.offset_y -= speed


    def fade(self):
        self.fade_surface.fill((0, 0, 0, self.fade_surface_alpha))
        change = 255 / ((self.fade_duration / 1000) * 60)
        
        if self.fade_type == "in":
            self.fade_surface_alpha += change
            if self.fade_surface_alpha >= 255:
                self.fading = False

        if self.fade_type == "out":
            self.fade_surface_alpha -= change
            if self.fade_surface_alpha <= 0:
                self.fading = False

                 
    def dialogue(self):
        if self.dialogue_manager.active:
            self.player.can_move = False
            self.dialogue_manager.box_x = (self.width - self.dialogue_manager.width) // 2
            self.dialogue_manager.box_y = self.height - self.dialogue_manager.height - 16

            self.dialogue_manager.update_dialogue(self.dt)
            self.dialogue_manager.update_arrow(self.dt)
        
            self.screen.blit(self.dialogue_manager.box, (self.dialogue_manager.box_x, self.dialogue_manager.box_y))
            self.dialogue_manager.get_text_surface(self.screen, self.dialogue_manager.box_x + 20, self.dialogue_manager.box_y + 20)

            if self.dialogue_manager.index >= len(self.dialogue_manager.message):
         
                if self.yes_no:
                    self.dialogue_manager.start_yes_no(self.screen)
                else:
                     self.dialogue_manager.draw_arrow(
                        self.screen,
                        self.dialogue_manager.box_x + self.dialogue_manager.width - self.dialogue_manager.arrow.get_width() - 20,
                        self.dialogue_manager.box_y + self.dialogue_manager.height - self.dialogue_manager.arrow.get_height() - 20)


    def stop_dialogue(self, entity):
        self.dialogue_manager.stop_arrow()
        self.dialogue_manager.active = False
        self.player.can_move = True
        self.player.following = False
        self.player.moving = False

        entity.speaking = False
        entity.event_just_reset = False
        entity.event_running = False

        self.condition_types(entity, getattr(entity, "active_event", None))
        entity.active_event = None

    def event_wait(self):
        if self.event_timer >= self.delay:
                self.event_timer = 0
                self.waiting = False
                self.delay = 0
            

    def player_follow_npc(self):
        
        if self.player.moving:
            if self.following_entity is not None:
                self.player.follow_npc(self.following_entity.world_x)

            if not self.player.moving and self.pending_move is not None:
                entity, x, y = self.pending_move

                entity.start_movement(x, y)

                self.pending_move = None
        else:
                if self.player.event_running:
                    if self.following_entity is not None:
                        self.player.following = True
                        self.player.direction = self.following_entity.direction
                        self.player.update_offsets(self.following_entity.direction_x, self.following_entity.direction_y)
                        
                        if self.player.following:
                            self.player.world_x = self.following_entity.world_x + self.player.offset_x
                            self.player.world_y = self.following_entity.world_y - 32 + self.player.offset_y

                
    def update_npc_events(self):
        for entity in self.tile_editor.entities:

            if self.waiting:
                self.event_wait()

            elif self.fading:
                self.fade()

            # normal movement when moving the npc
            elif entity.moving:
                entity.update_movement()
                
                if not entity.moving:

                    # if move_to_player is called
                    if entity.moving_to_player:
                        px = round(self.player.world_x / 32) * 32
                        py = round(self.player.world_y / 32) * 32

                        self.player.start_follow(px, py)
                        self.following_entity = entity
                        entity.moving_to_player = False

                    entity.direction = "left" if self.player.world_x < entity.world_x else "right"



            # if follow_player is called
            elif entity.going_to_player:
                entity.follow_player()

            # after reaching player, follow him    
            elif entity.following_player:
                
                entity.direction = self.player.direction
                self.player.can_move = True
                self.player.event_running = False

                entity.update_offsets(self.player.direction)
                entity.smooth_offsets()

                entity.world_x = self.player.world_x + entity.offset_x
                entity.world_y = self.player.world_y + entity.offset_y


                # once reached destination, stop handling
                follow_player = entity.event.get("follow_player")

                if follow_player:
                    dx = follow_player[0] * TILE_SIZE - int(entity.world_x)
                    dy = follow_player[1] * TILE_SIZE - int(entity.world_y)
                         
                    if abs(dx) < TILE_SIZE and abs(dy) < TILE_SIZE:
                        entity.world_x, entity.world_y = int(entity.world_x), int(entity.world_y)
                        entity.start_movement(round(dx), round(dy))
                        entity.following_player = False

            elif entity.speaking:
                self.dialogue()
                self.dialogue_entity = entity
                
            #end events here
            elif (
                entity.event_running
                and not entity.moving
                and not entity.going_to_player
                and not self.player.moving
                and not entity.following_player
                and not entity.speaking
                and not self.waiting
            ):
                self.end_npc_event(entity)
                
    def end_npc_event(self, entity):            
        if getattr(entity, 'event_just_reset', False): # checks if attribute event_just_reset in entity is true, if it doesnt have a value use False
            entity.event_just_reset = False
            return  # dont advance state, just bail
    
        self.player.can_move = True
        self.player.moving = False
        self.player.event_running = False
        self.player.following = False
        entity.event_running = False
        entity.moving_to_player = False
        entity.going_to_player = False

        self.condition_types(entity, getattr(entity, "active_event", None))
        entity.active_event = None
        
                
    def update(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z and self.dialogue_manager.active and self.dialogue_manager.index >= len(self.dialogue_manager.message):
                        if self.dialogue_entity is not None:
                            self.stop_dialogue(self.dialogue_entity)
                            self.yes_no = False
    
            self.tick()
            self.key_pressed()
            
            self.tile_editor.update()

            self.screen.fill((0, 0, 0))

            if self.player.visible:
                self.player.update(self.dt)
                self.collide_player()
                
            self.smooth_camera_offsets()
            self.set_camera_pos()

            self.draw_tiles()
            
            if self.tile_editor.editor:
                self.draw_cursor()
                
            self.draw_entities()
            self.draw_third_layer()

            
            if not self.tile_editor.editor:
                self.handle_entity_events()
                self.player_follow_npc()
                self.player.smooth_offsets()
                self.update_npc_events()
                
            if self.dialogue_manager.active:
                self.dialogue()

            if self.yes_no and self.dialogue_manager.index >= len(self.dialogue_manager.message):
                self.dialogue_manager.move_arrow(self.screen, self.dt)


            self.screen.blit(self.fade_surface, (0, 0))


            pygame.display.flip()


        pygame.quit()
