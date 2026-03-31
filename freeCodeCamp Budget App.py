class Category:
    def __init__(self, name):
        self.name = name
        self.ledger = []

    def __str__(self):
        title_line = 30 - len(self.name)
        half_amount = '*' * (title_line // 2)
        right_half = '*' * (title_line // 2)
        if len(self.name) % 2 == 1:
            right_half = half_amount + "*"
        print(f'{half_amount}{self.name}{right_half}')

        for line in self.ledger:
            desc = line['description'][:23]
            amount = line['amount']
            print(f"{desc.ljust(23)}{amount:>7.2f}")

        return f"Total: {self.get_balance():>.2f}"

    def deposit(self, amount, description=''):
        self.ledger.append({'amount': amount, 'description': description})

    def withdraw(self, amount, description=''):
        while self.check_funds(amount):
            self.ledger.append({'amount': -amount, 'description': description})
            return True
        return False

    def get_balance(self):
        total = 0
        if len(self.ledger) > 0:
            for item in self.ledger:
                total += item['amount']
            return total
        return 0

    def transfer(self, amount, other):
        while self.check_funds(amount):
            self.withdraw(amount, f"Transfer to {other.name}")
            other.deposit(amount, f"Transfer from {self.name}")
            return True
        return False

    def check_funds(self, amount):
        return False if amount > self.get_balance() else True


def create_spend_chart(categories):
    print("Percentage spent by category")
    total_spent = 0
    for line in categories.ledger:
        if line['amount'] < 0:
            total_spent += line['amount']
    # print(f"Total spent: {abs(total_spent)}")




cat = Category("Groceries")
auto = Category("Auto")
cat.deposit(1000, description="Bank deposit")
cat.deposit(125, description="Bank deposit")
cat.withdraw(150, description="Bread")
cat.withdraw(50, description="Avacados and Bread to make the toast")
cat.deposit(300, description="Bank deposit from savings")
cat.withdraw(150, description="More white bread")

print(cat)
print()
create_spend_chart(cat)