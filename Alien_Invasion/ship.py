import pygame

class Ship:
    def __init__(self, ai_game):
        """initializes ship and starting position"""
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # loads ship
        self.image = pygame.image.load("images/player_ship.png")

        # gets the ship's rectangle space
        self.rect = self.image.get_rect()

        # initializes ship at bottom-center of screen
        self.rect.midbottom = self.screen_rect.midbottom

        # stores a float for ship's horizontal position
        self.x = float(self.rect.x)
        # stores a float for ship's vertical position
        self.y = float(self.rect.y)

        # movement flag: start with a ship that's not moving
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def update(self):
        """updates ship position based on movement flags"""
        # updates ship's x value, not the rectangle
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        elif self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        elif self.moving_up and self.rect.top > 0:
            self.y -= self.settings.ship_speed
        elif self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.ship_speed

        # updates rectangle object from self.x and self.y
        self.rect.x = self.x
        self.rect.y = self.y

    def blitme(self):
        """draws ship at current location"""
        self.screen.blit(self.image, self.rect)