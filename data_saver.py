import pygame
import json
from tile_editor import TileEditor
from player import Player
from npc import NPC

class DataSaver:
    def __init__(self, tile_editor, player):
        self.tile_editor = tile_editor
        self.player = player

    def save_game(data, path):
        with open(path, "w") as f:
            json.dump(
                data,
                f,
                indent=4,
                sort_keys=True,
                ensure_ascii=False
            )

    def save_data(self):
        tile_dicts = []
        npc_data = {}

        for tile in self.tile_editor.tiles:
            tile_dicts.append({"x": tile.x_pos, "y": tile.y_pos, "id": tile.base_id, "layer": tile.layer})

        for entity in self.tile_editor.entities:
            if isinstance(entity, NPC):
                npc_data[entity.referral_code] = {
                    "x": entity.world_x,
                    "y": entity.world_y,
                    "state": entity.state,
                    "direction": entity.direction,
                    "npc_id": entity.npc_id,
                    "solid": entity.solid,
                    "event_state": entity.saved_event_state
                }
                
        data = {
            "tiles": tile_dicts,

            "player": {
                "world_x": self.player.world_x,
                "world_y": self.player.world_y,
                "state": self.player.state,
                "direction": self.player.direction
            },

            "camera_x": self.tile_editor.camera_x,
            "camera_y": self.tile_editor.camera_y
        }
        
        
        with open(r"C:\Users\hchok\OneDrive\Desktop\Python Projects\RPG Game\metadata\saved_data.json", "w") as file:
            pass
            json.dump(data, file, indent=4, sort_keys=True)


        with open(r"C:\Users\hchok\OneDrive\Desktop\Python Projects\RPG Game\metadata\npc_metadata.json", "w") as file:
            pass
            json.dump(npc_data, file, indent=4, sort_keys=True)



            
