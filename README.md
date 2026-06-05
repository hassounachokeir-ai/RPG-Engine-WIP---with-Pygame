# RPG-Engine-WIP---with-Pygame
This project is a functional RPG engine built with Python and Pygame. While the core systems are operational, several planned features such as combat, inventory management, and scene transitions are still under development.
<img width="954" height="536" alt="Recording 2026-06-05 072410" src="https://github.com/user-attachments/assets/6e341af4-105f-4269-90ac-06fb93d79eb9" />
<img width="956" height="536" alt="Recording 2026-06-05 072247" src="https://github.com/user-attachments/assets/9c22cd44-2e18-43ce-9037-673fab4c2395" />


Features CHecklist:
-Tile Editor ✓
-NPC Events ✓
-Player Movement ✓
-Saving and Loading ✓
-Full Entity System ✘ 
-Inventory System ✘
-Combat System ✘ 
-Enemies ✘ 
-Scenes ✘
-UI and Intro ✘ 

How to use:
1. Run main.py
0 - Toggle editor mode
H - Toggle hitbox mode
1 - Toggle layer
L - Change layer
2 - Toggle between placing NPCs and tiles
Left Click - Place tiles
Right Click - Remove tiles
Scroll Press - Copy tile
WASD - Move player
UP Arrow/ Down Arrow - Toggle between yes and no for choice dialogues
X - Interact with NPCs (outside of editor mode)
Z - End dialogue / Pick between yes and no
M - Save game state

How to edit metadata and sprites:

Tile Metadata:
-In tileset_test_metadata, change the value of the "image" key to the new tileset path. If you wish to edit the tileset, open sprites then tilset.png
-The "tiles" key contains a list of every single tile's properties. Typically, it is structured as follows: 
{"type": "empty", "animated": false}

"type": The type of hitbox the tile has, possible options are "full", "empty", "partial", or "custom". 
→ "full" automatically gives the tile a hitbox of the tile size (e.g. 16x16 or 32x32)
→ "empty" means the tile has no hitbox at all
→ "partial", if this is specified, add the key "hitbox":[x, y, width, height]. x and y are the x and y coordinates of the hitbox relative to the top left corner of the tile which is (0, 0). width is the width of the hitbox, whereas height is the height of the hitbox
→ "custom", if this is specified, add the key "hitbox":[[],[],[]...] Here, hitbox has a list with multiple lists in it. Each list is [x, y, width, height] which allows us to create a custom shaped hitbox.

"animated": Specifies whether the tile can animate or not
→ "false" means the tile doesnt animate
→ Should the tile have an animation add a list with the animation sequence, ONLY on the first tile of that sequence. (E.g. "animated": [12, 13, 14] on tile 12, but do not add this data to tiles 13 and 14, their "animated" must be false)

-Tile Index: The tileset is subsurfaced horizontally first, then vertically. That means it is split into rows, not coloumns. So a tileset of this structure (Each "[]" represents a tile):
[][][]
[][][]
[][][]
Would be subsurfaced like this:
[0][1][2]
[3][4][5]
[6][7][8]
And saved like this in the tile_surfaces list in tile_editor.py:
[0: Tile:{}. 1: Tile:{}...]

When editing the tileset metadata, the index of each entry represents the index of each tile in tile_surfaces. MAKE SURE to add {"type": "empty", "animated": false} fur transparent tiles which havent been filled out yet, otherwise the game will give you the wrong data. Although transparent tiles aren't shown in game and cannot be used to build with.

Entity Metadata:
-This section includes the basic data for any entity's sprite. This includes the image, the animation frames and the hitbox as well as the animation delay.
-To edit any entity's sprite, change the value of the "image" key of the respective entity to the new path, or open sprites and then edit the respective spritesheet.

"animation_frames": This is split into "idle", "run" and "delay".
"idle": A list containing the index of each frame of the idle animation.
"run": A list containing the index of each frame of the run animation. 
"delay": The delay between each frame of the animation in milliseconds.
"hitbox"[x, y, width, height]: Works exactly withn the tiles (tip: its best to have the hitbox sit at the sprite's lower body for smoother and more realistic collision)

-The spritehseets are subsurfaced just like the tiles, rows first.
-To add a new NPC, create a new entry in the "npcs" list.
-If you wish to add new entity types, you could do so by adding a new key, a new class for that entity which inherits from Entity, and configuring tile_editor.py and game.py for the placement, rendering and behaviour of that new entity.

-If you add a new spritesheet, make sure that it matches the dimensions of 16x32. If you wish to change that, change self.tile_width and self.tile_height in entity or the respective class.

Player Metadata:
player_metadata.json contains only 1 entry currently called "player_has_gold", this is currently only being used for testing purposes, more on that later.

NPC Metadata:
Each NPC has its own unique ID. Each NPC has the following entries: "direction", "event_state", "npc_id", "solid", "state", "x" and "y".

-"direction": The direction the NPC faces when the game loads, this is "right" by default. THe other option is "left".
-"npc_id": The id which refers to the id in the npcs list in entities_metadata. This tells the program what sprite to load, with what hitbox and what animation frames, delay and hitbox.
-"solid": Determines whether or not the NPC is collideable. Useful for blocking pathways and special events. TIP: If the NPC ever has to move towards or with the player, set this to false. Otherwise the NPC's hitbox will glitch with the player's hitbox.
-"state": Either "idle" or "run". Determines what the NPC is doing at the beginning of the game. Although this will most likely reset to "idle" anyways.
-"x" and "y": The world coordinates of the NPC.
-"event_state": A list of all the events the NPC carries out, more on that below.

"event_state" is split into 2 parts, the global event state and the local event states. The global event state is a global switch between all NPCs. This allows one NPC to affect another one remotely. The local event states are switches within the individual NPCs. This determines their chronological behaviour within a global event state. Heres how it's structured.

"global_event_state"{"local_event_state"{events}, "local_event_state"{events}}. "global_event_state"{....}

The global event state can be any nummber (as a string) or "all". "all" is the fallback which runs anyways regardless of the global event state. This is useful for avoiding repitition and copying behaviour over many global states. This can be overridden in other global states. That means local state "1" in global state "0" has a priority over "1" in "all".

The local event state is any number as a string. It is structured as follows:
{"condition": "none", "[event_type]":..., "next_event": "...", "trigger":...}

"condition": can be "none" or "player_has_gold", although the latter is used for testing purposes only. Depending on the condition, the following event is either run or not. Condition determines whether we advance or not. For more conditions, go into game.py and scroll down to condition_types().

"[event_type]": The main event the NPC does. Could be: "dialogue", "yes_no", "move", "move_to_player", "move_to_npc", "follow_player", "follow_npc", "visibility", "player_visibility", "wait", "fade", or "pan_camera"

-"dialogue": Set the value of this key to the dialogue you want the NPC to say. For breaking lines use "\n".
-"yes_no": If you use this event, get rid of "next_event" from the entry. Structured as follows: {"text":.., "yes_event": .., "no_event":..}. "text" funcitons just as dialogue, "yes_event" is the next local event we should go to if the player says yes, "no_event" is the opposite.
-"move":[x, y] : Moves the NPC by x and y tiles in the x and y direction respectively. x and y should be the number in TILES.
-"move_to_player":true : The value of this method is irrelevant. It moves the NPC to the player and faces him.
-"move_to_npc": true : The value of this method is irrelevant. It moves the player to the NPC.
-"follow_player": [x, y] : The NPC moves to the player and follows him to the tile(x, y). x and y are the coordinates in TILES.
-"follow_npc": [x, y] : The player mvoes to the NPC, and the NPC moves x and y tiles. The player stops following aftewards. x and y are the values in TILES.
-"visibility": Can be either true or false, makes the NPC either visible or invisible. If invisible, they keep updating but cannot interact with the player.
-"player_visibility": Can be either true or false, makes the player either visible or invisible. If invisible the player cannot move nor can he interact with NPCs.
"wait": Waits a certain amount before moving onto the next method. Time in milliseconds.
"fade": {"type":.., "duration"..}: Makes a black overlay fade in or out. "type" can be "in" or "out". "duration" is the duration of the fading in milliseconds.
"pan_camera": [x, y]: Pans the camera by x and y tiles. x and y are camera offsets, use [0, 0] to return them back to normal. Value in TILES.

-"next_event": The next event state the NPC switches to once the method is complete, this is a number as a string and can only be fufilled if the condition is true.

-"trigger": Determines how the NPC's event is triggered, can be either "interact", "see_player", or "automatic".
"interact": The player has to approach the NPC and press "X" to interact.
"see_player": If specified add the key "distance" with an integer as a value represting how many tiles away the NPC can detect you. (The NPC can also detect you if you are within a 1 tile distance in the y direction)
"automatic": The event runs automatically after the event before it is complete. Useful for a series of event which have to carry out after each other.

Settings:
In case you change the tileset tile size or want to down- or upscale your game, change the values of original_tile_size and SCALE. (Hitboxes and player sprite are affected by scale, so you csn configure your game with e.g. 16x16 tiles but upscale it with a scale of 2 later without any consequences) NOTE: for tile placement, only place the tiles after you have decided the scale, otherwise the coordinates will be wrong. (This is a WIP but an easy fix and will be fixed soon)


