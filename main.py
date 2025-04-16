import pygame
from screen_effect import ScreenEffects
from npc import SkeletonEnemy
from battle import BattleManager

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

from player import Player
from area_manager import AreaManager

# Load font
pixel_font_path = "fonts/PixelOperator.ttf"
font = pygame.font.Font(pixel_font_path, 28)

# Load player sprites
player_sprites = {
    "down": pygame.image.load("decals/character/player/down_sprite_sheet.png"),
    "up": pygame.image.load("decals/character/player/up_sprite_sheet.png"),
    "left": pygame.image.load("decals/character/player/left_sprite_sheet.png"),
    "right": pygame.image.load("decals/character/player/right_sprite_sheet.png"),
}

player_frame_width = player_sprites["down"].get_width() // 12
player_frame_height = player_sprites["down"].get_height()
player = Player(player_sprites, player_frame_width, player_frame_height, scale_factor=0.15, frame_delay=5)

area_manager = AreaManager(screen, WIDTH, HEIGHT, player)
battle_manager = BattleManager(screen)

def render_game():
    area_manager.draw()
    player.draw(screen)

running = True
active_npc = None
battle_mode = False

while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if not battle_mode:
                npc = area_manager.check_interactions()
                if npc:
                    if not npc.show_dialogue:
                        npc.show_dialogue = True
                        active_npc = npc
                    else:
                        npc.next_dialogue()
                else:
                    door_props = area_manager.get_nearby_door()
                    if door_props:
                        ScreenEffects.fade(screen, render_game, 500)
                        area_manager.load_stage(door_props["target_stage"])
                        player.x = float(door_props["target_x"])
                        player.y = float(door_props["target_y"])
                        ScreenEffects.fade(screen, render_game, 500)

    if not battle_mode and area_manager.current_stage == "stage3":
        for skel in area_manager.skeletons:
            dist = ((player.x - skel.x) ** 2 + (player.y - skel.y) ** 2) ** 0.5
            if dist < 200:
                battle_mode = True
                battle_manager.start_battle()

    screen.fill((0, 0, 0))

    if battle_mode:
        battle_manager.update()
        battle_manager.draw_battle_scene()
        battle_manager.draw_ui()
    else:
        area_manager.draw()
        if not active_npc or not active_npc.show_dialogue:
            player.update(keys)
        area_manager.update_npcs()
        player.draw(screen)

        if not active_npc:
            if area_manager.check_interactions() or area_manager.get_nearby_door():
                e_prompt = font.render("E to interact", True, (255, 255, 255))
                screen.blit(e_prompt, (player.x - 50, player.y - 60))

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