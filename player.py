import pygame

class Player:
    def __init__(self, sprite_sheets, frame_width, frame_height, scale_factor=1.2, frame_delay=3):
        """Player character with top-down movement (like Pokémon)."""
        self.sprite_sheets = sprite_sheets  # Dictionary storing sprite sheets for each direction
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale_factor = scale_factor  # Reduce this to make the character smaller
        self.frame_delay = frame_delay

        # Movement
        self.x = 300
        self.y = 300
        self.speed = 4  # Walking speed
        self.direction = "down"  # Default direction

        # Animation
        self.frames = {dir: self.load_frames(sprite_sheets[dir]) for dir in sprite_sheets}
        self.current_frame = 0
        self.tick_count = 0
        self.moving = False

    def load_frames(self, sprite_sheet):
        """Extracts frames from the sprite sheet."""
        sheet_width, sheet_height = sprite_sheet.get_size()
        num_frames = sheet_width // self.frame_width  # Calculate number of frames

        print(f"Extracting {num_frames} frames from sprite sheet with size: {sheet_width}x{sheet_height}")  # DEBUG

        frames = []
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height))
            scaled_frame = pygame.transform.scale(frame, (self.frame_width * self.scale_factor, self.frame_height * self.scale_factor))
            frames.append(scaled_frame)

        if not frames:
            print("ERROR: No frames extracted")  # DEBUG

        return frames


    def move(self, keys):
        """Handles 4-direction movement."""
        self.moving = False

        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = "left"
            self.moving = True

        elif keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = "right"
            self.moving = True

        elif keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = "up"
            self.moving = True

        elif keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = "down"
            self.moving = True

    def update(self, keys):
        """Updates movement and animation."""
        self.move(keys)

        if self.moving:
            self.tick_count += 1
            if self.tick_count >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
                self.tick_count = 0
        else:
            self.current_frame = 0  # Reset to idle frame when not moving

    def draw(self, screen):
        """Draws the player with the correct animation frame."""
        screen.blit(self.frames[self.direction][self.current_frame], (self.x, self.y))
