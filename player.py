import pygame

class Player:
    def __init__(self, sprites, frame_width, frame_height, scale_factor, frame_delay=3):
        self.sprites = sprites
        self.direction = "down"
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale_factor = scale_factor
        self.frame_delay = frame_delay

        self.x = 400
        self.y = 200
        self.current_frame = 0
        self.tick_count = 0
        self.moving = False

    def update(self, keys, screen_width=800, screen_height=600):
        speed = 5
        dx, dy = 0, 0
        self.moving = False

        if keys[pygame.K_LEFT]:
            dx = -speed
            self.direction = "left"
            self.moving = True
        elif keys[pygame.K_RIGHT]:
            dx = speed
            self.direction = "right"
            self.moving = True
        elif keys[pygame.K_UP]:
            dy = -speed
            self.direction = "up"
            self.moving = True
        elif keys[pygame.K_DOWN]:
            dy = speed
            self.direction = "down"
            self.moving = True

        next_x = self.x + dx
        next_y = self.y + dy

        buffer = 10
        if buffer <= next_x <= screen_width - buffer and buffer <= next_y <= screen_height - buffer:
            self.x = next_x
            self.y = next_y

        if self.moving:
            self.tick_count += 1
            if self.tick_count >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % 12
                self.tick_count = 0
        else:
            self.current_frame = 0  # reset to idle frame

    def draw(self, screen):
        sprite_sheet = self.sprites[self.direction]
        frame = sprite_sheet.subsurface(pygame.Rect(
            self.current_frame * self.frame_width, 0, self.frame_width, self.frame_height
        ))
        frame = pygame.transform.scale(frame, (
            int(self.frame_width * self.scale_factor), int(self.frame_height * self.scale_factor)
        ))
        screen.blit(frame, (
            self.x - (self.frame_width * self.scale_factor) / 2,
            self.y - (self.frame_height * self.scale_factor) / 2
        ))
