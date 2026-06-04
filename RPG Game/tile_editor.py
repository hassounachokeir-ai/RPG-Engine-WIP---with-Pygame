import pygame
import json
from tile import Tile
from player import Player
from settings import TILE_SIZE, SCALE, original_tile_size
from npc import NPC

tile_surfaces = []

def load_data():
    with open(r"C:\Users\hchok\OneDrive\Desktop\Python Projects\RPG Game\metadata\tileset_test_metadata.json", "r") as file:
                data = json.load(file)

    return pygame.image.load(data["image"]).convert_alpha(), data

tileset_image = None
data = None

def subsurface_sheet():
    tile_size = original_tile_size
    sheet_width = tileset_image.get_width()
    sheet_height = tileset_image.get_height()

    for y in range(0, sheet_height, tile_size):
        for x in range(0, sheet_width, tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            tile = tileset_image.subsurface(rect)
            new_tile = pygame.transform.scale(tile, (tile_size * SCALE, tile_size * SCALE))

            tile_surfaces.append(new_tile)

class TileEditor:
    def __init__(self, player):
        self.player = player
        
        global tileset_image, data
        tileset_image, data = load_data()
        subsurface_sheet()

        self.editor = True
        self.layer_toggle = True

        self.tiles = []
        self.tile_id = 1
        self.collided = False
        self.hitboxes = []
        self.hovering_tile = None
        self.layer = 0

        self.tileset_libraries = ("tiles", "npcs")
        self.lib_idx = 0
        self.tileset_library = self.tileset_libraries[self.lib_idx]

        self.entities = []
        self.hovering_entity = None
        self.npc_id = 0

        self.overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.overlay.fill((255, 255, 255, 50))

        self.tile_cursor = Tile(0, 0, self.tile_id, self.layer)
        self.npc_cursor = NPC(0, 0, "idle", "right", self.npc_id, referral_code=None)
        self.cursor = self.tile_cursor if self.tileset_library == "tiles" else self.npc_cursor
        self.grid_x = None
        self.grid_y = None

        self.target_offset_x = 0
        self.target_offset_y = 0
        self.offset_x = 0
        self.offset_y = 0

        self.camera_x = 0
        self.camera_y = 0
        self.cursor_x = 0
        self.cursor_y = 0
        
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(60)
        self.timer = 0
        
        self.read_data()

    def read_data(self):
        with open(r"C:\Users\hchok\OneDrive\Desktop\Python Projects\RPG Game\metadata\saved_data.json", "r") as file:
            tile_data = json.load(file)

        with open(r"C:\Users\hchok\OneDrive\Desktop\Python Projects\RPG Game\metadata\npc_metadata.json", "r") as file:
            npc_data = json.load(file)

        if npc_data is None:
            npc_data = {}


        tiles = tile_data.get("tiles", [])
        for t in tiles:
            self.tiles.append(Tile(t["x"], t["y"], t["id"], t["layer"]))

        for key, npc in npc_data.items():
            self.entities.append(NPC(npc["x"], npc["y"], npc["state"], npc["direction"], npc["npc_id"], key))

        self.camera_x = tile_data.get("camera_x", 0)
        self.camera_y = tile_data.get("camera_y", 0)

    def tick(self):
        self.dt = self.clock.tick(60)
        self.timer += self.dt

    def update_type(self):
        self.cursor = self.tile_cursor if self.tileset_library == "tiles" else self.npc_cursor
        
    def update_cursor(self):
        if self.tileset_library == "tiles":
            self.cursor.tile_id = self.tile_id

        elif self.tileset_library == "npcs":
            self.cursor.set_npc_id(self.npc_id)
    

    def update_collisions(self):
        self.hitboxes = []

        for tile in self.tiles:
        
            tile_data = data["tiles"][tile.base_id]
            collision_type = tile_data["type"]
            animation_type = tile_data["animated"]

            if collision_type == "full":
                self.hitboxes.append(pygame.Rect(tile.x_pos, tile.y_pos, TILE_SIZE, TILE_SIZE))

            elif collision_type == "partial":
                h = tile_data.get("hitbox", [0, 0, TILE_SIZE, TILE_SIZE]) #try to get hitbox, if it doesnt exist take 0, 0, 32, 32

                self.hitboxes.append(pygame.Rect(tile.x_pos + h[0] * SCALE, tile.y_pos + h[1] * SCALE, h[2] * SCALE, h[3] * SCALE))

            elif collision_type == "custom":
                h = tile_data.get("hitbox", [0, 0, TILE_SIZE, TILE_SIZE])
                
                for l in h:
                    self.hitboxes.append(pygame.Rect(tile.x_pos + l[0] * SCALE, tile.y_pos + l[1] * SCALE, l[2] * SCALE, l[3] * SCALE))

            elif collision_type == "empty":
                pass

            if animation_type == True:
                tile.tick(self.dt)
                tile.animate_tile(tile_data)

            elif animation_type == False:
                pass

    def get_mouse_pos(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_x = self.mouse_pos[0]
        self.mouse_y = self.mouse_pos[1]

    def get_grid_x(self):
        self.grid_x = ((self.mouse_x + self.camera_x) // TILE_SIZE) * TILE_SIZE

    def get_grid_y(self):
        self.grid_y = ((self.mouse_y + self.camera_y) // TILE_SIZE) * TILE_SIZE

    def get_cursor_pos(self):
        world_x = self.mouse_x + self.camera_x
        world_y = self.mouse_y + self.camera_y

        self.cursor_x = (world_x // TILE_SIZE) * TILE_SIZE
        self.cursor_y = (world_y // TILE_SIZE) * TILE_SIZE

    def occupied(self):
        if self.tileset_library == "tiles":
            for tile in self.tiles:
                
                if tile.x_pos == self.grid_x and tile.y_pos == self.grid_y and tile.layer == self.layer:
                    self.hovering_tile = tile
                    return True

            return False

        else:
            for entity in self.entities:
                
                if entity.world_x == self.grid_x and entity.world_y == self.grid_y:
                    self.hovering_entity = entity
                    return True

            return False

    def mouse_clicked(self):
        buttons = pygame.mouse.get_pressed()

        if self.tileset_library == "tiles":
        
            if buttons[0]:
                if not self.occupied():
                    self.tiles.append(Tile(self.grid_x, self.grid_y, self.cursor.tile_id, self.layer))
                    print(self.tile_id)
                else:
                    if self.hovering_tile is not None:
                        self.hovering_tile.tile_id = self.cursor.tile_id

            if buttons[1]:
                if self.occupied():
                    self.cursor.tile_id = self.hovering_tile.tile_id
                    self.tile_id = self.cursor.tile_id

            if buttons[2]:
                if self.occupied():
                    self.tiles.remove(self.hovering_tile)

        elif self.tileset_library == "npcs":

            if buttons[0]:
                if not self.occupied():
                    self.entities.append(NPC(self.grid_x, self.grid_y, "idle", "right", self.cursor.npc_id, self.cursor.generate_id()))
                else:
                    if self.hovering_entity is not None:
                        self.entities.remove(self.hovering_entity)
                        self.entities.append(NPC(self.grid_x, self.grid_y, "idle", "right", self.cursor.npc_id, self.cursor.generate_id()))

            if buttons[2]:
                if self.occupied():
                    self.entities.remove(self.hovering_entity)


                        
    def is_empty(self, tile):
        for x in range(tile.get_width()):
            for y in range(tile.get_height()):
                if tile.get_at((x, y)).a != 0:
                    return False
        return True

    def toggle_layer(self):
        if self.layer_toggle:
            self.overlay.fill((255, 255, 255, 50))
        else:
            self.overlay.fill((255, 255, 255, 0))
            
    def key_pressed(self):
        keys = pygame.key.get_pressed()

        if self.timer >= 200:
            if keys[pygame.K_0]:
                self.timer = 0
                self.layer_toggle = False
                self.toggle_layer()
                self.editor = not self.editor
                print(f"Editor: {self.editor}")

            
            if self.editor:
                if keys[pygame.K_2]:
                    self.timer = 0
                    
                    self.lib_idx = (self.lib_idx + 1) % len(self.tileset_libraries)
                    
                    self.tileset_library = self.tileset_libraries[self.lib_idx]

                    self.update_type()
                
                if keys[pygame.K_n]:
                    self.timer = 0
                        
                    if self.tileset_library == "tiles":
                                
                        self.tile_id = (self.tile_id + 1) % len(tile_surfaces)

                        while self.is_empty(tile_surfaces[self.tile_id]):
                            self.tile_id = (self.tile_id + 1) % len(tile_surfaces)
                            
                    elif self.tileset_library == "npcs":
                        self.npc_id = (self.npc_id + 1) % len(self.npc_cursor.data["npcs"])

                    self.update_type()

                if keys[pygame.K_p]:
                    self.timer = 0

                    if self.tileset_library == "tiles":
                            
                        self.tile_id = (self.tile_id - 1) % len(tile_surfaces)

                        while self.is_empty(tile_surfaces[self.tile_id]):
                            self.tile_id = (self.tile_id + -1) % len(tile_surfaces)

                    elif self.tileset_library == "npcs":
                        self.npc_id = (self.npc_id - 1) % len(self.npc_cursor.data["npcs"])

                    self.update_type()

                if keys[pygame.K_l]:
                    self.timer = 0
                    
                    self.layer = (self.layer + 1) % 3
                    print(f"Layer: {self.layer}")

                if keys[pygame.K_1]:
                    self.timer = 0
                    self.layer_toggle = not self.layer_toggle
                    print(f"Layer: {self.layer_toggle}")


    def get_tile_surfaces(self):
        return tile_surfaces
                

    def update(self):
        self.tick()
        self.key_pressed()
        self.update_collisions()

        if self.editor:
            self.get_mouse_pos()
            self.update_cursor()
            self.get_grid_x()
            self.get_grid_y()
            self.get_cursor_pos()

            self.toggle_layer()

            self.mouse_clicked()

