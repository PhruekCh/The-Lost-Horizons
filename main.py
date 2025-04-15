import pygame
from player import Player
from area_manager import AreaManager

# Initialize Pygame
pygame.init()

# Screen Setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Load Font
pixel_font_path = "fonts/PixelOperator.ttf"
pixel_font_size = 28
font = pygame.font.Font(pixel_font_path, pixel_font_size)

# Load Player Walking Sprites
player_sprites = {
    "down": pygame.image.load("decals/character/player/down_sprite_sheet.png"),
    "up": pygame.image.load("decals/character/player/up_sprite_sheet.png"),
    "left": pygame.image.load("decals/character/player/left_sprite_sheet.png"),
    "right": pygame.image.load("decals/character/player/right_sprite_sheet.png"),
}

# Player Sprite Info
player_frame_width = player_sprites["down"].get_width() // 12
player_frame_height = player_sprites["down"].get_height()
player_scale_factor = 0.15

# Create Player Object
player = Player(player_sprites, player_frame_width, player_frame_height, player_scale_factor, frame_delay=3)

# ✅ Create AreaManager instance
area_manager = AreaManager(screen, WIDTH, HEIGHT, player)

# Game Loop
running = True
active_npc = None  # Track which NPC is showing dialogue

while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # NPC Interaction
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            npc = area_manager.check_interactions()
            if npc:
                if not npc.show_dialogue:
                    npc.show_dialogue = True
                    active_npc = npc
                else:
                    npc.next_dialogue()

    # ✅ Stage transition & only clear dialogue when stage changes
    stage_changed = area_manager.handle_stage_transition()
    if stage_changed:
        active_npc = None

    area_manager.draw()
    if not active_npc or not active_npc.show_dialogue:
        player.update(keys)  # ✅ Prevent movement during dialogue
    area_manager.update_npcs()
    player.draw(screen)

    # Dialogue box
    if active_npc and active_npc.show_dialogue:
        pygame.draw.rect(screen, (0, 0, 0), (100, 450, 600, 100))
        pygame.draw.rect(screen, (255, 255, 255), (105, 455, 590, 90))
        text_surface = font.render(active_npc.dialogue[active_npc.dialogue_index], True, (0, 0, 0))
        screen.blit(text_surface, (120, 480))
    else:
        active_npc = None

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
