class GameCharacter:
    def __init__(self, name):
        self._name = name
        self._health = 100
        self._mana = 50
        self._level = 1

    def __str__(self):
        return f"""Name: {self._name}
Level: {self._level}
Health: {self._health}
Mana: {self._mana}"""

    @property
    def name(self):
        return self._name

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, num):
        if num < 0:
            self._health = 0
        elif 100 >= num >= 0:
            self._health = num

    @property
    def mana(self):
        return self._mana

    @mana.setter
    def mana(self, num):
        if num < 0:
            self._mana = 0
        elif 50 >= num >= 0:
            self._mana = num

    @property
    def level(self):
        return self._level

    def level_up(self):
        self._level += 1
        self.health = 100
        self.mana = 50
        print(f"{self._name} leveled up to {self._level}!")
