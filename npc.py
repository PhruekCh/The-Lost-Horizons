import pygame

class NPC:
    def __init__(self, sprite_sheet, x, y, scale_factor=1.2, frame_delay=5, flip_horizontal=False):
        self.sprite_sheet = sprite_sheet
        if flip_horizontal:
            self.sprite_sheet = pygame.transform.flip(self.sprite_sheet, True, False)
        self.frames_per_row = 8  # 8 frames per row
        self.rows = 6  # 6 rows for different directions
        self.scale_factor = scale_factor
        self.frame_delay = frame_delay


        # NPC Position
        self.x = x
        self.y = y
        self.direction = "down"  # Default direction

        # Sprite Sheet Info
        self.sheet_width, self.sheet_height = self.sprite_sheet.get_size()
        self.frame_width = self.sheet_width // self.frames_per_row
        self.frame_height = self.sheet_height // self.rows
        self.num_frames = self.frames_per_row  # Only 8 frames per direction

        # Load Animation Frames
        self.frames = self.load_frames()
        self.current_frame = 0
        self.tick_count = 0

        # Expanded Dialogue System
        self.dialogue = [
            "Hello there!",
            "I see you are new here.",
            "Press 'E' again to continue.",
            "Be careful, this place is dangerous...",
            "Good luck!"
        ]
        self.dialogue_index = 0  # Track the current dialogue line
        self.show_dialogue = False  # Flag for showing dialogue

    def load_frames(self):
        """Extracts frames for each direction from an 8x6 sprite sheet."""
        frames = {"down": [], "left": [], "right": [], "up": []}
        directions = ["down", "left", "right", "up"]

        for i, direction in enumerate(directions):
            row = i  # Each direction takes one row in the sprite sheet
            for col in range(self.frames_per_row):
                frame = self.sprite_sheet.subsurface(
                    pygame.Rect(col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
                )
                scaled_frame = pygame.transform.scale(
                    frame, (int(self.frame_width * self.scale_factor), int(self.frame_height * self.scale_factor))
                )
                frames[direction].append(scaled_frame)

        return frames

    def update(self):
        """Updates NPC animation."""
        self.tick_count += 1
        if self.tick_count >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.tick_count = 0

    def draw(self, screen):
        """Draws the NPC on screen."""
        screen.blit(self.frames[self.direction][self.current_frame], (self.x, self.y))

    def check_interaction(self, player):
        distance = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5
        return distance < getattr(self, "interaction_range", 50)


    def next_dialogue(self):
        """Advances dialogue when the player presses E."""
        if self.dialogue_index < len(self.dialogue) - 1:
            self.dialogue_index += 1
        else:
            self.show_dialogue = False  # Close dialogue if at the last message
            self.dialogue_index = 0  # Reset to start when reopened
