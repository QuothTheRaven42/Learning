from abc import ABC, abstractmethod

"""
Does the method need access to instance data (self)?
├── YES → Does it need to enforce implementation?
│         ├── YES → @abstractmethod
│         └── NO  → Is it accessed like an attribute?
│                   ├── YES → @property
│                   └── NO  → Regular method (no decorator)
└── NO  → Does it need access to class data (cls)?
          ├── YES → @classmethod
          └── NO  → @staticmethod
"""

class Vehicle(ABC):
    _total_vehicles = 0

    def __init__(self, make, year):
        self._make = make
        self._year = year
        Vehicle._total_vehicles += 1

    # ───── @property: Controlled attribute access ─────
    @property
    def make(self):
        return self._make

    @property
    def age(self):
        """Computed property"""
        return 2024 - self._year

    # ───── @classmethod: Alternative constructor ──────
    @classmethod
    def from_string(cls, vehicle_string):
        """Creates instance from 'make-year' format"""
        make, year = vehicle_string.split("-")
        return cls(make, int(year))

    @classmethod
    def total_vehicles(cls):
        return cls._total_vehicles

    # ───── @staticmethod: Utility function ────────────
    @staticmethod
    def is_valid_year(year):
        return 1886 <= year <= 2024

    # ───── @abstractmethod: Enforced contract ─────────
    @abstractmethod
    def start_engine(self):
        pass

    @abstractmethod
    def fuel_type(self):
        pass


class ElectricCar(Vehicle):
    def start_engine(self):
        return "Silent electric motor started 🔋"

    def fuel_type(self):
        return "Electric"


class GasCar(Vehicle):
    def start_engine(self):
        return "Vroom vroom! 🔥"

    def fuel_type(self):
        return "Gasoline"
python
# --- Usage ---

# @staticmethod — no instance needed
print(Vehicle.is_valid_year(2020))          # True
print(Vehicle.is_valid_year(1500))          # False

# @classmethod — alternative constructor
tesla = ElectricCar.from_string("Tesla-2022")
ford  = GasCar.from_string("Ford-2018")

# @property — access like attributes
print(tesla.make)                           # Tesla
print(tesla.age)                            # 2
print(ford.make)                            # Ford
print(ford.age)                             # 6

# @abstractmethod — enforced implementations
print(tesla.start_engine())                 # Silent electric motor started 🔋
print(ford.start_engine())                  # Vroom vroom! 🔥

# @classmethod — class-level state
print(Vehicle.total_vehicles())             # 2

# ❌ Can't instantiate abstract class
# v = Vehicle("Test", 2020)                 # TypeError!