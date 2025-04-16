import pygame
from npc import NPC, SkeletonEnemy
import pytmx
from pytmx.util_pygame import load_pygame


TILE_SCALE = 1.5

class AreaManager:
    def __init__(self, screen, width, height, player):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height
        self.player = player


        self.tmx_maps = {
            "stage1": load_pygame("decals/bg/stage1.tmx"),
            "stage2": load_pygame("decals/bg/stage2.tmx"),
            "stage3": load_pygame("decals/bg/stage3.tmx"),
            "stage5": load_pygame("decals/bg/stage1.tmx")
        }

        self.current_stage = "stage1"
        self.tmx_data = None
        self.npcs = []
        self.doors = []
        self.collision_layer = None

        self.load_stage(self.current_stage)

    def load_stage(self, stage_name):
        self.current_stage = stage_name
        self.tmx_data = self.tmx_maps[stage_name]
        self.npcs = self.spawn_npcs_for_stage(stage_name)
        self.doors = self.load_doors_from_map()
        self.collision_layer = self.find_collision_layer()
        self.skeletons = []
        if stage_name == "stage3":
            self.skeletons.append(SkeletonEnemy("decals/character/skeleton/Idle.png", 400, 100))

    def find_collision_layer(self):
        for layer in self.tmx_data.layers:
            if hasattr(layer, 'name') and "collision" in layer.name.lower():
                return layer
        return None

    def is_blocked(self, x, y):
        if not self.collision_layer:
            return False

        tile_x = int(x // (self.tmx_data.tilewidth * TILE_SCALE))
        tile_y = int(y // (self.tmx_data.tileheight * TILE_SCALE))

        try:
            gid = self.collision_layer.data[tile_x][tile_y]
            tile_props = self.tmx_data.get_tile_properties_by_gid(gid)
            if tile_props and tile_props.get("collidable"):
                return True
        except:
            return False

        return False

    def spawn_npcs_for_stage(self, stage_name):
        npc_data = {
            "stage1": [
                ("aya", (300, 180), ["Meow!!", "You finally wake up, meow.",
                                    "I'm not sure how did we got here.",
                                    "This place seems dangerous y'know.",
                                    "At the very least, I know how to fight",
                                    "I gonna come with you, So you don't die here.",
                                    "My name is Aya, ya'know",
                                    "Anyway, let's find way out of here."], 50)
            ],
            "stage2": [
                ("delt", (200, 200), ["Where wwha, What is this place!",
                                        "Who are you guys", "alright, sorry I was too nervous",
                                        "I'm Delt nice to meet you",
                                        "You guys seem know how to fight, yea?",
                                        "I think we should stick together, I mean right?"], 60, 50, True)
            ],
            "stage5": [
                ("lancer", (100, 150), ["Hey! don't come any closer", "Stage 5 initiated"], 100, 50)
            ],
        }

        npc_list = []
        for npc_entry in npc_data.get(stage_name, []):
            if len(npc_entry) == 6:
                name, (x, y), dialogue, interaction_range, offset_x, flip = npc_entry
            elif len(npc_entry) == 5:
                name, (x, y), dialogue, interaction_range, offset_x = npc_entry
                flip = False
            else:
                name, (x, y), dialogue, interaction_range = npc_entry
                offset_x = 0
                flip = False

            sprite = pygame.image.load(f"decals/character/{name}.png")
            npc = NPC(sprite, x * TILE_SCALE, y * TILE_SCALE, scale_factor=2, frame_delay=3, flip_horizontal=flip)
            npc.dialogue = dialogue
            npc.interaction_range = interaction_range * TILE_SCALE
            npc.interaction_offset_x = offset_x * TILE_SCALE
            npc_list.append(npc)

        return npc_list

    def load_doors_from_map(self):
        doors = []
        for obj in self.tmx_data.objects:
            if obj.name == "door":
                door_rect = pygame.Rect(
                    obj.x * TILE_SCALE,
                    obj.y * TILE_SCALE,
                    obj.width * TILE_SCALE,
                    obj.height * TILE_SCALE
                )
                props = obj.properties
                doors.append((door_rect, props))
        return doors

    def draw(self):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        scaled_tile = pygame.transform.scale(
                            tile,
                            (int(tile.get_width() * TILE_SCALE), int(tile.get_height() * TILE_SCALE))
                        )
                        self.screen.blit(scaled_tile, (
                            int(x * self.tmx_data.tilewidth * TILE_SCALE),
                            int(y * self.tmx_data.tileheight * TILE_SCALE)
                        ))

        for npc in self.npcs:
            npc.draw(self.screen)
        for skeleton in self.skeletons:
            skeleton.draw(self.screen)

    def update_npcs(self):
        for npc in self.npcs:
            npc.update()
        for skeleton in self.skeletons:
            skeleton.update()

    def check_interactions(self):
        for npc in self.npcs:
            adjusted_npc_x = npc.x + getattr(npc, "interaction_offset_x", 0)
            distance = ((adjusted_npc_x - self.player.x) ** 2 + (npc.y - self.player.y) ** 2) ** 0.5
            interaction_range = getattr(npc, "interaction_range", 50)
            if distance < interaction_range:
                return npc
        return None

    def get_nearby_door(self):
        player_rect = pygame.Rect(
            self.player.x - (self.player.frame_width * self.player.scale_factor) / 2,
            self.player.y - (self.player.frame_height * self.player.scale_factor) / 2,
            self.player.frame_width * self.player.scale_factor * TILE_SCALE,
            self.player.frame_height * self.player.scale_factor * TILE_SCALE
        )

        for door_rect, props in self.doors:
            if door_rect.colliderect(player_rect.inflate(10, 10)):
                return props
        return None

    def handle_stage_transition(self):
        buffer = 10
        direction = None
        if self.player.x < -buffer:
            direction = "left"
        elif self.player.x > self.WIDTH - buffer:
            direction = "right"
        elif self.player.y < buffer:
            direction = "up"
        elif self.player.y > self.HEIGHT - buffer:
            direction = "down"

        if direction and direction in self.area_links[self.current_stage]:
            next_stage = self.area_links[self.current_stage][direction]
            self.load_stage(next_stage)

            if direction == "left":
                self.player.x = self.WIDTH - 50
            elif direction == "right":
                self.player.x = 10
            elif direction == "up":
                self.player.y = self.HEIGHT - 50
            elif direction == "down":
                self.player.y = 10

            return True

        return False