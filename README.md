# RPG-Engine-WIP---with-Pygame
The following is an RPG engine built entirely using Pygame and Python. The engine isn't complete yet, these are the following features: -Tile Editor, Adding and modifying NPCs, Saving and Loading, Moving aorund and colliding

To use add all the games to one file, enter the metadata and update all the file paths, then open dialgoue manager and update the respective file paths.

Controls: 
0 To enter editor mode, o to exit afterwards
1 To toggle layer mode (shows a white highlight over the activated layers)
L in editor mode to switch layers (There are 3 layers, 0, 1 and 2)
2 To switch to placing NPCs. 2 to switch again
N to change the current tile index  by 1
P to change the current tile index by -1
Left Click to place tiles
Right Click to remove tiles
Press the scroll button to choose or "copy" the hovering tile
WASD to move the player in both modes
M to save game state

Open  entity_metadata to add new entities and edit their sprites
Open npc_metadata to edit NPC events (for npc events open game.py and scroll to NPC Event Handling, entity_events())
Open tileset_test_metadata to edit tile properties (for tile properties open tile_editor.py)
