import pygame
import random
from screen_effect import ScreenEffects
from npc import Enemy, NPC


class BattleManager:
    def __init__(self, screen, heroes, exit_battle_callback, frame_delay=3):
        self.screen = screen
        self.heroes = heroes
        self.enemy = None
        self.available_elements = ["fire", "wind", "water"]
        self.selected_index = 0
        self.font = pygame.font.Font("fonts/PixelOperator.ttf", 24)
        self.team_hp = 300
        self.max_team_hp = 300
        self.damage = 30
        self.turn_ready = True
        self.cooldown_timer = 0
        self.cooldown_duration = 300
        self.exit_battle_callback = exit_battle_callback
        self.frame_delay = frame_delay
        self.selecting_element = True
        self.available_elements = ["fire", "wind", "water"]
        self.move_names = ["Element Attack", "Quick Attack", "Charge Up", "Heal"]
        self.selected_index = 0
        self.battle_bg = pygame.image.load("decals/bg/fightscene.jpg").convert()
        self.battle_bg = pygame.transform.scale(self.battle_bg, (screen.get_width(), screen.get_height()))
        self.waiting_for_continue = False
        self.battle_log = ""
        self.input_cooldown = 0
        self.input_cooldown_duration = 700
        self.turn_phase = "player_turn"
        self.charge_ready = False
        self.enemy_charge_ready = False
        self.dialogue_start_time = 0
        self.dialogue_cooldown = 500
        self.dialogue_step = None
        self.element_effect = None
        self.player_hit_effect = None
        self.element_effect_paths = {
            "fire": "decals/effect/fire.png",
            "wind": "decals/effect/wind.png",
            "water": "decals/effect/water.png"}
        self.normal_effect = "decals/effect/normal.png"
        self.crit_rate = 0.2
        self.battle_stats = {
            "turns": 0,
            "player_dmg": 0,
            "enemy_dmg": 0,
            "quick": 0,
            "charge": 0,
            "heal": 0,
            "dmg_received": 0,
            "elemental": 0,
            "element_type": [],
            "element_dmg": {
                "fire": 0,
                "wind": 0,
                "water": 0
            },
            "quick_dmg": 0,
            "charge_dmg": 0,
            "heal_amount": 0,
            "crits": 0
        }


    def start_battle(self, name, idle_image, attack_image, element_type, frame_count, attack_frame_count, hp):
        self.enemy = Enemy(
        name=name,
        image_path=idle_image,
        x=600,
        y=320,
        scale=2.7,
        frame_count=frame_count,
        element_type=element_type,
        attack_image_path=attack_image,
        attack_frame_count=attack_frame_count,
        frame_delay=5,
        max_hp = hp
    )
        self.enemy.crit_rate = 0.2

    def handle_input(self, event):
        if self.turn_phase == "wait" and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            now = pygame.time.get_ticks()
            if now - self.dialogue_start_time < self.dialogue_cooldown:
                return

            if self.dialogue_step == "element":
                self.dialogue_step = None
                self.turn_phase = "player_turn"
                self.battle_log = ""

            elif self.dialogue_step == "player":
                self.dialogue_step = "enemy"
                self.dialogue_start_time = pygame.time.get_ticks()
                self.enemy_attack()

            elif self.dialogue_step == "enemy":
                self.dialogue_step = None
                self.turn_phase = "player_turn"
                self.waiting_for_continue = False
                self.battle_log = ""

            if self.enemy and self.enemy.hp <= 0 and self.turn_phase != "end":
                self.enemy.hp = 0
                self.battle_log = "Enemy defeated!"
                self.turn_phase = "end"
                pygame.time.set_timer(pygame.USEREVENT, 0)
                ScreenEffects.fade(self.screen, lambda: None, 500)
                self.exit_battle_callback()
                from data_plotter import save_battle_record
                save_battle_record(self.battle_stats.copy())

            return

        if not self.turn_ready:
            return

        if event.type == pygame.KEYDOWN:
            if self.selecting_element:
                # ELEMENT SELECT PHASE
                if self.input_cooldown == 0:
                    if event.key == pygame.K_LEFT:
                        self.selected_index = (self.selected_index - 1) % 3
                        self.input_cooldown = self.input_cooldown_duration
                    elif event.key == pygame.K_RIGHT:
                        self.selected_index = (self.selected_index + 1) % 3
                        self.input_cooldown = self.input_cooldown_duration
                    if event.key == pygame.K_RETURN:
                        self.player_element = self.available_elements[self.selected_index]
                        self.battle_log = f"Selected {self.player_element.upper()} element!"
                        self.selecting_element = False
                        self.selected_index = 0
                        self.turn_phase = "wait"
                        self.dialogue_step = "element"
                        self.dialogue_start_time = pygame.time.get_ticks()
                        self.turn_ready = False
                        pygame.time.set_timer(pygame.USEREVENT, 500)
            else:
                if self.waiting_for_continue:
                    if event.key == pygame.K_RETURN and self.turn_ready:
                        self.waiting_for_continue = False
                        self.enemy_attack()
                        self.turn_phase = "wait"

                        self.turn_ready = False
                        pygame.time.set_timer(pygame.USEREVENT, 500)
                else:
                    if self.input_cooldown == 0:
                        if event.key == pygame.K_LEFT:
                            self.selected_index = (self.selected_index - 1) % 4
                            self.input_cooldown = self.input_cooldown_duration
                        elif event.key == pygame.K_RIGHT:
                            self.selected_index = (self.selected_index + 1) % 4
                            self.input_cooldown = self.input_cooldown_duration
                    if event.key == pygame.K_RETURN and self.turn_ready:
                        self.use_move(self.selected_index)
                        if self.turn_phase == "wait" and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            now = pygame.time.get_ticks()
                            if now - self.dialogue_start_time < self.dialogue_cooldown:
                                return
                            self.waiting_for_continue = False
                            self.turn_phase = "player_turn"
                            self.battle_log = ""
                            return


    def perform_attack(self):
        selected_element = self.player_element
        self.battle_log = f"You attacked with {selected_element.upper()}!"

        advantage = {
            "fire": "wind",
            "wind": "water",
            "water": "fire"
        }

        if advantage[selected_element] == self.enemy.element_type:
            damage = self.damage * 1.5
            self.battle_log += " It's super effective!"
        elif advantage[self.enemy.element_type] == selected_element:
            damage = self.damage * 0.75
            self.battle_log += " It's not very effective."
        else:
            damage = self.damage

        if random.random() < self.crit_rate:
            damage *= 1.5
            self.battle_stats["crits"] += 1  # ✅ track it!
            self.battle_log += " CRITICAL HIT!"

        if self.enemy is None:
            return

        self.enemy.hp -= damage
        self.battle_log += f" Dealt {int(damage)} dmg."

        print(f"Enemy HP: {self.enemy.hp}")

        if self.enemy.hp <= 0:
            self.enemy.hp = 0
            self.battle_log = ""
            self.exit_battle_callback()

        self.turn_ready = False
        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def enemy_attack(self):

        if self.enemy:
            self.enemy.is_attacking = True
            if self.enemy_charge_ready:
                base = random.randint(20, 50)
                damage = int(base * 1.5)
                self.battle_log = f"The enemy unleashes a CHARGED attack! Your team takes {damage} dmg."
                self.enemy_charge_ready = False
            else:
                if random.random() < 0.5:
                    self.enemy_charge_ready = True
                    self.battle_log = "The enemy is charging up for a powerful attack!"
                    damage = 0
                else:
                    damage = random.randint(20, 50)
                    self.battle_log = f"Enemy attacks! Your team takes {damage} dmg."

            self.team_hp -= damage
            self.battle_stats["enemy_dmg"] += damage
            self.battle_stats["dmg_received"] += damage

            if damage > 0:
                if self.enemy.name == "Kitsune":
                    self.player_hit_effect = ElementEffect(
                    "decals/effect/water.png", 6, 2, scale=5, offset=(0, 0))
                else:
                    self.player_hit_effect = ElementEffect(
                        self.normal_effect, 6, 2, scale=5, offset=(0, 0))

            if self.team_hp <= 0:
                self.team_hp = 0
                self.battle_log += " Your team is defeated!"
                self.turn_phase = "end"
                self.dialogue_step = None
                ScreenEffects.fade(self.screen, lambda: None, 500)
                self.exit_battle_callback()
            else:
                self.waiting_for_continue = True

            self.dialogue_step = "enemy"
            self.turn_phase = "wait"
            self.dialogue_start_time = pygame.time.get_ticks()

    def draw_ui(self):
        team_hp_text = self.font.render(f"Team HP: {self.team_hp}/{self.max_team_hp}", True, (255, 255, 255))
        self.screen.blit(team_hp_text, (50, 100))

        if self.enemy:
            enemy_hp_text = self.font.render(f"Enemy HP: {self.enemy.hp}/{self.enemy.max_hp}", True, (255, 255, 255))
            self.screen.blit(enemy_hp_text, (500, 100))

        if self.selecting_element:
            for i, element in enumerate(self.available_elements):
                color = (255, 0, 0) if i == self.selected_index else (255, 255, 255)
                text = self.font.render(element.upper(), True, color)
                self.screen.blit(text, (300 + i * 100, 500))

        else:
            for i, move in enumerate(self.move_names):
                color = (255, 0, 0) if i == self.selected_index else (255, 255, 255)
                text = self.font.render(move, True, color)
                self.screen.blit(text, (150 + i * 170, 530))

        if self.battle_log:
            pygame.draw.rect(self.screen, (128, 128, 128), (100, 200, 600, 80))
            pygame.draw.rect(self.screen, (255, 255, 255), (105, 205, 590, 70))

            log_text = self.font.render(self.battle_log, True, (0, 0, 0))
            self.screen.blit(log_text, (120, 230))


    def update(self):
        for hero in self.heroes:
            hero.update()
        if self.enemy:
            self.enemy.update()
        if self.input_cooldown > 0:
            self.input_cooldown -= self.frame_delay * (1000 / 30)
            if self.input_cooldown < 0:
                self.input_cooldown = 0

    def draw(self):
        self.screen.blit(self.battle_bg, (0, 0))
        for hero in self.heroes:
            hero.draw(self.screen)
        if self.enemy:
            self.enemy.draw(self.screen)
            if self.element_effect:
                self.element_effect.update()
                if self.enemy:
                    self.element_effect.draw(self.screen, self.enemy.x, self.enemy.y - 40)
                if self.element_effect.finished:
                    self.element_effect = None
            if self.player_hit_effect:
                self.player_hit_effect.update()
                if self.heroes:
                    hero = self.heroes[0]
                    self.player_hit_effect.draw(self.screen, hero.x, hero.y)
                if self.player_hit_effect.finished:
                    self.player_hit_effect = None



    def trigger_element_effect(self, use_special=True):
        if use_special:
            effect_path = self.element_effect_paths.get(self.player_element)
        else:
            effect_path = self.normal_effect
        if effect_path:
            self.element_effect = ElementEffect(effect_path, 6, 2, scale=4, offset=(-40, 100))

    def use_move(self, move_index):
        self.battle_stats["turns"] += 1
        if self.turn_phase != "player_turn":
            return

        if move_index == 0:
            self.battle_log = "You used Special Attack!"
            self.trigger_element_effect()
            self.perform_attack()
            

            self.battle_stats["elemental"] += 1
            self.battle_stats["element_type"].append(self.player_element)

            estimated_damage = self.damage
            advantage = {
                "fire": "wind",
                "wind": "water",
                "water": "fire"
            }
            if self.enemy:
                if advantage[self.player_element] == self.enemy.element_type:
                    estimated_damage *= 1.5
                elif advantage[self.enemy.element_type] == self.player_element:
                    estimated_damage *= 0.75

            if self.enemy is None:
                return
            if random.random() < self.crit_rate:
                estimated_damage *= 2

            self.battle_stats["element_dmg"][self.player_element] += int(estimated_damage)
            self.battle_stats["player_dmg"] += int(estimated_damage)


        elif move_index == 1:
            self.battle_log = "You used Quick Attack!"
            self.trigger_element_effect(use_special=False)
            if hasattr(self.enemy, "crit_rate"):
                self.enemy.crit_rate = max(0, self.enemy.crit_rate - 0.1)
            dmg = int(self.damage * 0.75)
            self.enemy.hp -= dmg
            self.battle_stats["quick"] += 1
            self.battle_stats["quick_dmg"] += dmg
            self.battle_stats["player_dmg"] += dmg

        elif move_index == 2:
            if self.charge_ready:
                self.battle_log = "Charge released!"
                self.trigger_element_effect(use_special=False)
                dmg = int(self.damage * 0.75 * 2.5)
                self.enemy.hp -= dmg
                self.battle_stats["charge_dmg"] += dmg
                self.battle_stats["charge"] += 1
                self.battle_stats["player_dmg"] += dmg
                self.charge_ready = False
            else:
                self.battle_log = "Charging up..."
                self.charge_ready = True

        elif move_index == 3:
            self.battle_log = "Team healed!"
            heal_amount = 70
            self.team_hp = self.team_hp + heal_amount
            self.player_hit_effect = ElementEffect("decals/effect/heal.png", 6, 2, scale=4, offset=(0, 0))
            self.battle_stats["heal"] += 1
            self.battle_stats["heal_amount"] += heal_amount

        self.turn_phase = "wait"
        self.dialogue_start_time = pygame.time.get_ticks()
        self.turn_ready = False
        self.dialogue_step = "player"
        pygame.time.set_timer(pygame.USEREVENT, 500)


class ElementEffect:
    def __init__(self, image_path, columns, rows, scale=1.0, offset=(0, 0)):
        self.sheet = pygame.image.load(image_path).convert_alpha()
        self.columns = columns
        self.rows = rows
        self.scale = scale
        self.offset = offset

        self.frame_width = self.sheet.get_width() // columns
        self.frame_height = self.sheet.get_height() // rows

        self.frames = []
        for row in range(rows):
            for col in range(columns):
                rect = pygame.Rect(
                    col * self.frame_width,
                    row * self.frame_height,
                    self.frame_width,
                    self.frame_height
                )
                frame = self.sheet.subsurface(rect)
                if scale != 1.0:
                    frame = pygame.transform.scale(
                        frame,
                        (int(self.frame_width * scale), int(self.frame_height * scale))
                    )
                self.frames.append(frame)

        self.index = 0
        self.timer = 0
        self.finished = False

    def update(self):
        self.timer += 1
        if self.timer % 2 == 0:
            self.index += 1
            if self.index >= len(self.frames):
                self.finished = True

    def draw(self, screen, x, y):
        if not self.finished:
            offset_x, offset_y = self.offset
            frame = self.frames[self.index]
            screen.blit(frame, (x + offset_x, y + offset_y))
