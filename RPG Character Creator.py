from random import randint

class Character:

    @property
    def char_sheet(self):
        char_sheet = f"""\n{self.name} - {self.race} {self.__class__.__name__.lower()}
---------------------------------
        Health: {self.life_total}/{self.health}
        Strength: {self.strength}
        Dexterity: {self.dexterity}
        Constitution: {self.constitution}
        Intelligence: {self.intelligence}
        Wisdom: {self.wisdom}
        Charisma: {self.charisma}\n"""
        return char_sheet

    def __init__(self):
        self.life_total = 0
        self.name = input("What is your character's name? ").title()
        self.race = input("\nChoose a race:\n--------\nDwarf\nElf\nGnome\nHalfling\nHuman\n").title()
        self.health = randint(8,20)
        self.strength = randint(5, 15)
        self.dexterity = randint(5, 15)
        self.constitution = randint(5, 15)
        self.intelligence = randint(5, 15)
        self.wisdom = randint(5, 15)
        self.charisma = randint(5, 15)
        self.passed_out = False
        self.level = 1
        self.exp = 0

        if self.race == "Human":
            self.strength += 1
            self.constitution += 1
            self.intelligence += 1
            self.wisdom += 1
            self.charisma += 1
        elif self.race == "Dwarf":
            self.strength += 2
            self.constitution += 2
            self.wisdom += 1
        elif self.race == "Elf":
            self.dexterity += 2
            self.intelligence += 1
            self.wisdom += 1
            self.charisma += 1
        elif self.race == "Gnome":
            self.dexterity += 2
            self.intelligence += 2
            self.constitution += 1
        elif self.race == "Halfling":
            self.dexterity += 2
            self.constitution += 1
            self.charisma += 2


    def __str__(self):
        return self.char_sheet

    def gain_exp(self):
        if self.passed_out == True:
            return f'{self.name} the {self.__class__.__name__.lower()} is passed out and cannot gain experience.'
        self.exp += 10
        print(f'{self.name} the {self.__class__.__name__.lower()} has gained 10 experience points and has {self.exp} total.')
        if self.exp >= 50 * self.level:
            self.exp = 0
            self.level += 1
            print(f'\n{self.name} has gained a level...')
            print(f'They are now level {self.level}!')
            self.health += 3
            self.strength += 1
            self.dexterity += 1
            self.constitution += 1
            self.intelligence += 1
            self.wisdom += 1
            self.charisma += 1
            self.life_total = self.health
        print()

    def take_dmg(self, dmg):
        if self.life_total > 0:
            self.life_total -= dmg
        if self.passed_out == True:
            return f'{self.name} the {self.__class__.__name__.lower()} is passed out and cannot take damage.'
        elif self.life_total <= 0:
            self.life_total = 0
            self.passed_out = True
            print(f'{self.name} the {self.__class__.__name__.lower()} is passed out!')
            print(f'Life total: {self.life_total}/{self.health}')
        else:
            print(f'{self.name} the {self.__class__.__name__.lower()} has taken {dmg} points of damage!')
            print(f'Remaining life for {self.name}: {self.life_total}/{self.health}')

    def rest(self):
        print('\nResting up......')
        self.life_total = self.health
        self.passed_out = False
        print(f'{self.name} the {self.__class__.__name__.lower()} is rested up and ready to go!')
        print(f'Life total: {self.life_total}/{self.health}')

    def cause_dmg(self, target):
        if self.passed_out == True:
            print(f'{self.name} the {self.__class__.__name__.lower()} is passed out and cannot attack.')
            return 0
        elif target.passed_out == True:
            print(f'{self.name} has already won! {target.name} is passed out and cannot be attacked.')
            return 0
        else:
            dmg = randint(1,5)
            print(f'{self.name} the {self.__class__.__name__.lower()} attacks for {dmg} hp!')
            target.take_dmg(dmg)
            self.gain_exp()
            return dmg

    def display_sheet(self):
        print(f'Your new character sheet for {self.name} the {self.__class__.__name__.lower()}:')
        print(f'{self.char_sheet}')

class Barbarian(Character):
    def __init__(self):
        super().__init__()
        self.strength += 3
        self.constitution += 3
        self.intelligence -= 3
        self.life_total = self.health
        display_sheet(self)


class Cleric(Character):
    def __init__(self):
        super().__init__()
        self.constitution += 3
        self.wisdom += 3
        self.charisma -= 3
        self.life_total = self.health
        self.display_sheet()

class Wizard(Character):
    def __init__(self):
        super().__init__()
        self.wisdom += 3
        self.charisma += 3
        self.health -= 3
        self.life_total = self.health
        self.display_sheet()

class Sorcerer(Character):
    def __init__(self):
        super().__init__()
        self.intelligence += 3
        self.health += 3
        self.wisdom -= 3
        self.life_total = self.health
        self.display_sheet()

class Fighter(Character):
    def __init__(self):
        super().__init__()
        self.strength += 3
        self.charisma += 3
        self.wisdom -= 3
        self.life_total = self.health
        self.display_sheet()

class Rogue(Character):
    def __init__(self):
        super().__init__()
        self.dexterity += 3
        self.intelligence += 3
        self.constitution -= 3
        self.life_total = self.health
        self.display_sheet()

