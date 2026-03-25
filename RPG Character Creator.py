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

        # Race bonuses
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

        # Starting inventory
        self.inventory = {'50 ft rope':1, 'small health potion':4, 'torch': 2, 'water':3, 'rations':1}

    def __str__(self):
        return self.char_sheet

    @property
    def char_sheet(self) -> str:
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

    def display_sheet(self) -> None:
        print(f'\nYour character sheet for {self.name} the {self.__class__.__name__.lower()}:')
        print(f'{self.char_sheet}')

    def export_char_sheet(self) -> None:
        with open(f"{self.name}_the_{self.race}_{self.__class__.__name__}_lvl{self.level}.txt", "w") as file:
            file.write(self.char_sheet)
            file.write('\n')
            file.write('Inventory:\n')
            lines = "\n".join(f"{value} {key}" for key, value in self.inventory.items())
            file.write(f'{lines}')
        print(f'Character sheet for {self.name} the {self.__class__.__name__.lower()} has been saved as {self.name}_the_{self.race}_{self.__class__.__name__}_lvl{self.level}.txt.')

    def gain_exp(self, multiplier=1) -> str | None:
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

    def take_dmg(self, dmg) -> None:
        if self.life_total > 0:
            self.life_total -= dmg
        if self.passed_out == True:
            print(f'{self.name} the {self.__class__.__name__.lower()} is passed out and cannot take damage.')
        elif self.life_total <= 0:
            self.life_total = 0
            self.passed_out = True
            print(f'{self.name} the {self.__class__.__name__.lower()} took {dmg} damage and has passed out!\n')
            print(f'Life total: {self.life_total}/{self.health}')
        else:
            print(f'{self.name} the {self.__class__.__name__.lower()} has taken {dmg} points of damage!')
            print(f'Remaining life for {self.name}: {self.life_total}/{self.health}\n')

    def rest(self) -> None:
        print('\nResting up......')
        self.life_total = self.health
        self.passed_out = False
        print(f'{self.name} the {self.__class__.__name__.lower()} is rested up and ready to go!')
        print(f'Life total: {self.life_total}/{self.health}\n')

    def cause_dmg(self, target) -> int:
        if self.passed_out == True:
            print(f'{self.name} the {self.__class__.__name__.lower()} is passed out and cannot attack.')
            return 0
        elif target.passed_out == True:
            print(f'{self.name} has already won! {target.name} is passed out and cannot be attacked.')
            return 0
        else:
            dmg = Character.roll_dice(6)
            print(f'{self.name} the {self.__class__.__name__.lower()} attacks for {dmg} hp!')
            target.take_dmg(dmg)
            self.gain_exp()
            return dmg

    def use_item(self, item) -> None:
        if item not in self.inventory:
            print(f"{item} is not {self.name}'s inventory.\n")
        elif self.inventory[item] == 1:
            del self.inventory[item]
            print(f'{self.name} the {self.__class__.__name__.lower()} used {item} from their inventory.')
        else:
            self.inventory[item] -= 1
            print(f'{self.name} the {self.__class__.__name__.lower()} used {item} from their inventory.')
            print(f'There are {self.inventory[item]} {item} left in the inventory.')

        # healing items
        if item == 'small health potion':
            num = Character.roll_dice(6)
            self.life_total = min(self.life_total + num, self.health)
            print(f'small health potion used - +{num} health gained!')
            print(f'Life total: {self.life_total}\n')
            self.passed_out = False
        elif item == 'large health potion':
            num = Character.roll_dice(20) + Character.roll_dice(6)
            self.life_total = min(self.life_total + num, self.health)
            print(f'large health potion used - +{num} health gained!')
            print(f'Life total: {self.life_total}\n')
            self.passed_out = False

    def add_item(self, item) -> None:
        if item in self.inventory:
            self.inventory[item] += 1
        else:
            self.inventory[item] = 1
        print(f'{item} added to the inventory.')

    def view_inventory(self) -> None:
        if self.inventory:
            lines = "\n".join(f"{value} {key}" for key, value in self.inventory.items())
            print(f"{self.name}'s inventory:\n{lines}\n")
        else:
            print(f"No items in {self.name}'s inventory.\n")

    @staticmethod
    def roll_dice(d_num) -> int:
        return randint(1, d_num)


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
        self.dexterity -= 3
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


"""
Next steps:
-------------
Spells or abilities
Monster class
dictionary mapping the races to bonus stats instead of if/elif block
@property setter for life_total, auto sets passed_out when at 0, cleaning up logic from take_dmg
Class attributes for things like base_health or hit_die
simple while loop for combat
"""
