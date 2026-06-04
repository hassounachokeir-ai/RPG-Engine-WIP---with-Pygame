import pygame

class Tile:
    def __init__(self, x_pos, y_pos, tile_id, layer):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.base_id = tile_id
        self.tile_id = tile_id
        self.layer = layer

        self.timer = 0

    def tick(self, dt):
        self.timer += dt

    def __repr__(self):
        return f"Tile({self.x_pos}, {self.y_pos}, {self.tile_id}, {self.layer})"

    def animate_tile(self, data):
        frame_delay = 100
        animation = data.get("animation", [])

        frame_count = len(animation)

        if self.timer >= frame_delay:
            self.timer = 0

            start = animation[0]

            current_index = self.tile_id - start
            current_index = (current_index + 1) % frame_count

            self.tile_id = start + current_index
