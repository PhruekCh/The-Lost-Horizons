import pygame

class ScreenEffects:
    def fade(screen, fade_in=True, duration=1000):
        fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
        fade_surface.fill((0, 0, 0))
        clock = pygame.time.Clock()

        steps = 30
        for i in range(steps + 1):
            alpha = int(255 * (i / steps)) if fade_in else int(255 * (1 - i / steps))
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            clock.tick(1000 // duration * steps)

