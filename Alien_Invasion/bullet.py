import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """A class to manage bullets fire from the ship."""

    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # creates a bullet rect at (0, 0) and sets correct position
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # stores bullet's position as a float
        self.y = float(self.rect.y)
        self.x = float(self.rect.x)

    def update(self):
        """Move bullet up the screen."""
        # updates exact position of bullet
        self.y -= self.settings.bullet_speed
        # update the rectangle position
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw bullet on screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)
