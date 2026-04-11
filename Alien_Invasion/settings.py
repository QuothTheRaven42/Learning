class Settings:
    def __init__(self):
        # screen settings
        self.screen_width = 1920
        self.screen_height = 1080
        self.bg_color = (50,100,150)

        # ship settings
        self.ship_speed = 1.5

        # bullet settings
        self.bullet_speed = 2.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60,60,60)
        self.bullets_allowed = 3

        # alien settings
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        # fleet_direct of 1 represents right; -1 represents left
        self.fleet_direction = 1