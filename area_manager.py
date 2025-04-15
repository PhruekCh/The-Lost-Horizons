import pygame
from npc import NPC

class AreaManager:
    def __init__(self, screen, width, height, player):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height
        self.player = player

        self.area_links = {
            "stage1": {"left": "stage5", "right": "stage2", "down": "stage3"},
            "stage2": {"left": "stage1"},
            "stage3": {"up": "stage1"},
            "stage5": {"right": "stage1"},
        }

        self.backgrounds = {
            "stage1": pygame.image.load("decals/bg/stage1.png"),
            "stage2": pygame.image.load("decals/bg/b1.png"),
            "stage3": pygame.image.load("decals/bg/b2.jpg"),
            "stage5": pygame.image.load("decals/bg/b3.jpg"),
        }

        self.current_stage = "stage1"
        self.background = None
        self.npcs = []

        self.load_stage(self.current_stage)

    def load_stage(self, stage_name):
        self.current_stage = stage_name
        self.background = pygame.transform.scale(self.backgrounds[stage_name], (self.WIDTH, self.HEIGHT))
        self.npcs = self.spawn_npcs_for_stage(stage_name)

    def spawn_npcs_for_stage(self, stage_name):
        # Each entry can have an optional interaction_range and optional offset
        npc_data = {
            "stage1": [
                ("cat", (400, 300), ["Meow!", "This is stage 1"], 50)
            ],
            "stage2": [
                ("priest", (200, 250), ["Hi!", "Welcome to stage 2"], 70, 0, True)
            ],
            "stage5": [
                ("lancer", (100, 150), ["Hey! don't come any closer", "Stage 5 initiated"], 100, 50)
            ],
        }

        npc_list = []
        for npc_entry in npc_data.get(stage_name, []):
    # Support 6-tuple: name, pos, dialogue, range, offset_x, flip
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
            npc = NPC(sprite, x, y, scale_factor=2, frame_delay=3, flip_horizontal=flip)
            npc.dialogue = dialogue
            npc.interaction_range = interaction_range  # ✅ Custom interaction range
            npc.interaction_offset_x = offset_x  # ✅ Optional offset for fine-tuning interaction zone
            npc_list.append(npc)

        return npc_list

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for npc in self.npcs:
            npc.draw(self.screen)

    def update_npcs(self):
        for npc in self.npcs:
            npc.update()

    def check_interactions(self):
        for npc in self.npcs:
            print(f"Checking NPC at ({npc.x}, {npc.y}) with player at ({self.player.x}, {self.player.y})")
            adjusted_npc_x = npc.x + getattr(npc, "interaction_offset_x", 0)
            distance = ((adjusted_npc_x - self.player.x) ** 2 + (npc.y - self.player.y) ** 2) ** 0.5
            interaction_range = getattr(npc, "interaction_range", 50)
            if distance < interaction_range:
                return npc
        return None

    def handle_stage_transition(self):
        buffer = 10
        direction = None

        sprite_height = self.player.frame_height * self.player.scale_factor

        if self.player.x < -buffer:
            direction = "left"
        elif self.player.x > self.WIDTH - buffer:
            direction = "right"
        elif self.player.y < buffer:  # 🟢 FIXED: use buffer for top
            direction = "up"
        elif self.player.y > self.HEIGHT - buffer:  # 🟢 FIXED: use HEIGHT - buffer
            direction = "down"

        if direction and direction in self.area_links[self.current_stage]:
            next_stage = self.area_links[self.current_stage][direction]
            self.load_stage(next_stage)

            # Reset player position
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

