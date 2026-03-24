from random import randint

class Character:

    def __init__(self):
        self.life_total = 0
        self.name = input(f"What is your {self.__class__.__name__.lower()}'s name? ").title()
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

        self.inventory = ['50 ft rope', 'small health potion', 'small health potion', 'small health potion', 'small health potion', 'torch', 'water' , 'water' , 'water' , 'rations']

    def __str__(self):
        return self.char_sheet

    @property
    def char_sheet(self):
        char_sheet = f"""\n{self.name} - {self.race} {self.__class__.__name__.lower()} - level {self.level}
---------------------------------
    Health: {self.life_total}/{self.health}
    Strength: {self.strength}
    Dexterity: {self.dexterity}
    Constitution: {self.constitution}
    Intelligence: {self.intelligence}
    Wisdom: {self.wisdom}
    Charisma: {self.charisma}\n"""
        return char_sheet

    def display_sheet(self):
        print(f'\nYour character sheet for {self.name} the {self.__class__.__name__.lower()}:')
        print(f'{self.char_sheet}')


    def gain_exp(self, multiplier=1):
        if self.passed_out == True:
            return f'{self.name} the {self.__class__.__name__.lower()} is passed out and cannot gain experience.'
        mult_value = 10 * multiplier
        self.exp += mult_value
        print(f'{self.name} the {self.__class__.__name__.lower()} has gained {mult_value} experience points and has {self.exp} total.')
        if self.exp >= 50 * self.level:
            self.exp = 0
            self.level += 1
            print(f'\n{self.name} has gained a level...')
            print(f'They are now level {self.level}!\n')
            self.health += round(2.5 * (self.constitution * 0.1))
            self.strength += round(1 * (self.strength * 0.08))
            self.dexterity += round(1 * (self.dexterity * 0.08))
            self.constitution += round(1 * (self.constitution * 0.08))
            self.intelligence += round(1 * (self.intelligence * 0.08))
            self.wisdom += round(1 * (self.wisdom * 0.08))
            self.charisma += round(1 * (self.charisma * 0.08))
            self.life_total = self.health

    def take_dmg(self, dmg):
        if self.life_total > 0:
            self.life_total -= dmg
        if self.passed_out == True:
            return f'{self.name} the {self.__class__.__name__.lower()} is passed out and cannot take damage.'
        elif self.life_total <= 0:
            self.life_total = 0
            self.passed_out = True
            print(f'{self.name} the {self.__class__.__name__.lower()} is passed out!\n')
            print(f'Life total: {self.life_total}/{self.health}')
        else:
            print(f'{self.name} the {self.__class__.__name__.lower()} has taken {dmg} points of damage!')
            print(f'Remaining life for {self.name}: {self.life_total}/{self.health}\n')

    def rest(self):
        print('\nResting up......')
        self.life_total = self.health
        self.passed_out = False
        print(f'{self.name} the {self.__class__.__name__.lower()} is rested up and ready to go!')
        print(f'Life total: {self.life_total}/{self.health}\n')

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

    def use_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            print(f'{self.name} the {self.__class__.__name__.lower()} used {item} from their inventory!\n')
        else:
            print(f'{item} is not in the inventory.\n')

    def view_inventory(self):
        items = ", ".join(self.inventory) if self.inventory else f"No items in {self.name}'s inventory."
        return f"{self.name}'s inventory:\n{items}\n"


    @staticmethod
    def roll_d4():
        return randint(1, 4)

    @staticmethod
    def roll_d6():
        return randint(1, 6)

    @staticmethod
    def roll_d20():
        return randint(1, 20)

class Barbarian(Character):
    def __init__(self):
        super().__init__()
        self.strength += 3
        self.constitution += 3
        self.intelligence -= 3
        self.life_total = self.health
        self.display_sheet()


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
        self.intelligence += 3
        self.charisma += 3
        self.health -= 3
        self.life_total = self.health
        self.display_sheet()

class Sorcerer(Character):
    def __init__(self):
        super().__init__()
        self.wisdom += 3
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

sorcerer = Sorcerer()

sorcerer.gain_exp()
sorcerer.gain_exp()
sorcerer.gain_exp(multiplier=Character.roll_d4())
sorcerer.gain_exp(multiplier=Character.roll_d6())
sorcerer.gain_exp(multiplier=Character.roll_d20())

sorcerer.take_dmg(10)
sorcerer.take_dmg(10)
sorcerer.take_dmg(10)
sorcerer.take_dmg(10)

print(sorcerer.char_sheet)
print(sorcerer.view_inventory())

sorcerer.rest()

sorcerer.use_item('50 ft rope')
sorcerer.use_item('water')
sorcerer.use_item('potato')

print(sorcerer.view_inventory())


"""
Next steps:
-------------
* Add inventory methods
* @staticmethod for dice roller

dictionary mapping the races to bonus stats instead of if/elif block
@property setter for life_total, auto sets passed_out when at 0, cleaning up logic from take_dmg
Class attributes for things like base_health or hit_die
Spells or abilities
Monster class
Save/load character sheets with File I/O
simple while loop for combat
"""
