import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """A class to represent a single alien."""

    def __init__(self, ai_game):
        """Initialise the alien abd set starting position."""

        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # loads alien image and sets its rect attribute
        self.image = pygame.image.load('images/enemy_1.png')
        self.rect = self.image.get_rect()

        # starts new aliens near the top left of the screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # stores aliens' exact horizontal position
        self.x = float(self.rect.x)

    def check_edges(self):
        """Return True if the alien is at its edge of screen."""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self):
        """Move alien to the right or left."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x

