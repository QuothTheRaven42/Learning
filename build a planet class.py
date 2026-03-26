class Planet:
    def __init__(self, name, planet_type, star):
        if type(name) != str or type(planet_type) != str or type(star) != str:
            raise TypeError('name, planet type, and star must be strings')
        elif name == '' or planet_type == '' or star == '':
            raise ValueError('name, planet_type, and star must be non-empty strings')

        self.name = name
        self.planet_type = planet_type
        self.star = star

    def __str__(self):
        return f'Planet: {self.name} | Type: {self.planet_type} | Star: {self.star}'

    def orbit(self):
        return f'{self.name} is orbiting around {self.star}...'


planet_1 = Planet('Earth', 'Watery', 'the sun')
planet_2 = Planet('Venus', 'Stormy', 'the sun')
planet_3 = Planet('Mercury', 'Rocky', 'the sun')

print(planet_1)
print(planet_2)
print(planet_3)

print(planet_1.orbit())
print(planet_2.orbit())
print(planet_3.orbit())

# venus = Planet('Venus', 'round', 'sun')
# print(venus)
# print(venus.orbit())