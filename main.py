import pygame
from screen_effect import ScreenEffects
from npc import Enemy, NPC
from battle import BattleManager
from data_plotter import open_stats_window

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

from player import Player
from area_manager import AreaManager

pygame.mixer.init()
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.load("sound/main_theme.mp3")
pygame.mixer.music.play(-1)
current_theme = "main_theme"

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
heroes = [
    NPC(pygame.image.load("decals/character/aya.png"), 80, 400, scale_factor=2.3, frame_delay=3),
    NPC(pygame.image.load("decals/character/delt.png"), 150, 400, scale_factor=2.3, frame_delay=3)
]

def exit_battle():
    global battle_mode, current_theme  # ✅ FIXED
    battle_mode = False
    battle_manager.enemy = None
    area_manager.enemy.clear()
    battle_manager.team_hp = battle_manager.max_team_hp
    
    ScreenEffects.fade(screen, render_game, 500)

    if current_theme != "monster_theme":
        pygame.mixer.music.load("sound/monster_theme.mp3")
        pygame.mixer.music.play(-1)
        current_theme = "monster_theme"




battle_manager = BattleManager(screen, heroes, exit_battle)

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
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_0:
            open_stats_window()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if not battle_mode:
                npc = area_manager.check_interactions()
                if npc:
                    if not npc.show_dialogue:
                        npc.show_dialogue = True
                        active_npc = npc
                    else:
                        npc.next_dialogue()
                elif area_manager.get_nearby_key():
                    open_stats_window()
                else:
                    door_props = area_manager.get_nearby_door()
                    if door_props:
                        ScreenEffects.fade(screen, render_game, 500)
                        area_manager.load_stage(door_props["target_stage"])
                        stage = door_props["target_stage"]
                        area_manager.load_stage(stage)

                        if stage not in ["stage3", "stage4","stage5", "stage6","stage7"]:
                            if current_theme != "main_theme":
                                pygame.mixer.music.load("sound/main_theme.mp3")
                                pygame.mixer.music.play(-1)
                                current_theme = "main_theme"
                        else:
                            if current_theme != "monster_theme":
                                pygame.mixer.music.load("sound/monster_theme.mp3")
                                pygame.mixer.music.play(-1)
                                current_theme = "monster_theme"

                        
                        player.x = float(door_props["target_x"])
                        player.y = float(door_props["target_y"])
                        ScreenEffects.fade(screen, render_game, 500)


    def battleenemy(stage:str, name:str, idle_image:str, attack_image:str,
                    element_type:str, frame_count:int, attack_frame_count:int, hp:int):
        global battle_mode
        if not battle_mode and area_manager.current_stage == stage:
            for skel in area_manager.enemy:
                dist = ((player.x - skel.x) ** 2 + (player.y - skel.y) ** 2) ** 0.5
                if dist < 200:
                    ScreenEffects.fade(screen, fade_in=True, duration=300)
                    battle_mode = True
                    battle_manager.start_battle(name = name, idle_image = idle_image,
                    attack_image = attack_image, element_type = element_type,frame_count = frame_count
                    , attack_frame_count = attack_frame_count, hp = hp)
                    pygame.mixer.music.load("sound/battle_theme.mp3")
                    pygame.mixer.music.play(-1)
                    current_theme = "battle_theme"
                    ScreenEffects.fade(screen, fade_in=True, duration=300)

    battleenemy("stage3", "Skeleton", "decals/character/skeleton/Idle.png",
             "decals/character/skeleton/Attack.png","fire", 7, 5, hp=200)

    battleenemy("stage4", "Samurai", "decals/character/samurai/Idle.png",
             "decals/character/samurai/Attack.png","wind", 6, 5, hp=250)

    battleenemy("stage5", "Kitsune", "decals/character/kitsune/Idle.png",
             "decals/character/kitsune/Attack.png","water", 8, 7, hp=270)

    battleenemy("stage6", "Satyr", "decals/character/satyr/Idle.png",
             "decals/character/satyr/Attack.png","fire", 7, 8, hp=250)

    battleenemy("stage7", "Gorgon", "decals/character/gorgon/Idle.png",
             "decals/character/gorgon/Attack.png","wind", 7, 10, hp=250)

    screen.fill((0, 0, 0))


    if battle_mode:
        battle_manager.handle_input(event)
        battle_manager.update()
        battle_manager.draw()
        battle_manager.draw_ui()
        if event.type == pygame.USEREVENT:
            battle_manager.turn_ready = True
            pygame.time.set_timer(pygame.USEREVENT, 0)

    else:
        area_manager.draw()
        if not active_npc or not active_npc.show_dialogue:
            player.update(keys)
        area_manager.update_npcs()
        player.draw(screen)

        if not active_npc:
            if area_manager.check_interactions() or area_manager.get_nearby_door() or area_manager.get_nearby_key():
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