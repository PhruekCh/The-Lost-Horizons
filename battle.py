import pygame
from screen_effect import ScreenEffects
from npc import SkeletonEnemy, NPC

class BattleManager:
    def __init__(self, screen):
        self.screen = screen
        self.heroes = []
        self.enemy = None
        self.started = False

    def start_battle(self):
        ScreenEffects.fade(self.screen, self.draw_battle_scene, duration=500)
        self.started = True

        self.heroes = [
            NPC(pygame.image.load("decals/character/aya.png"), 100, 300, scale_factor=2, frame_delay=3),
            NPC(pygame.image.load("decals/character/delt.png"), 100, 400, scale_factor=2, frame_delay=3)]
        self.enemy = SkeletonEnemy("decals/character/skeleton/Idle.png", 600, 350, scale=2, frame_count=7)
        self.enemy.frames = [pygame.transform.flip(f, True, False) for f in self.enemy.frames]

        ScreenEffects.fade(self.screen, self.draw_battle_scene, duration=500)

    def update(self):
        for hero in self.heroes:
            hero.update()
        if self.enemy:
            self.enemy.update()

    def draw_battle_scene(self):
        self.screen.fill((30, 30, 30))  # Battle background
        for hero in self.heroes:
            hero.draw(self.screen)
        if self.enemy:
            self.enemy.draw(self.screen)

    def draw_ui(self):
        font = pygame.font.SysFont("Arial", 28)
        text = font.render("[Attack]  [Skill]  [Guard]", True, (255, 255, 255))
        self.screen.blit(text, (200, 500))
