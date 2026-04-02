class Category:
    def __init__(self, name):
        self.name = name
        self.ledger = []

    def __str__(self):
        title_line = 30 - len(self.name)
        half_amount = '*' * (title_line // 2)
        right_half = '*' * (title_line // 2)
        total = []
        # In case self.name is an odd length
        if len(self.name) % 2 == 1:
            right_half += "*"
        total.append(f'{half_amount}{self.name}{right_half}')

        for line in self.ledger:
            desc = line['description'][:23]
            amount = line['amount']
            total.append(f"{desc:<23}{amount:>7.2f}")
        total.append(f"Total: {self.get_balance():>.2f}")
        return "\n".join(total)

    def deposit(self, amount, description=''):
        self.ledger.append({'amount': amount, 'description': description})

    def withdraw(self, amount, description='') -> bool:
        while self.check_funds(amount):
            self.ledger.append({'amount': -amount, 'description': description})
            return True
        return False

    def get_balance(self) -> int:
        total = 0
        if len(self.ledger) > 0:
            for item in self.ledger:
                total += item['amount']
            return total
        return 0

    def transfer(self, amount, other) -> bool:
        while self.check_funds(amount):
            self.withdraw(amount, f"Transfer to {other.name}")
            other.deposit(amount, f"Transfer from {self.name}")
            return True
        return False

    def check_funds(self, amount) -> bool:
        return False if amount > self.get_balance() else True

# Not yet fully implemented
def create_spend_chart(categories: list) -> str:
    total_spent = 0
    current = 0
    each_total = []

    # calculate total spent and spent by individual categories
    for each in categories:
        for item in each.ledger:
            for value in item.values():
                if isinstance(value, (int, float)) and value < 0:
                    total_spent += value
                    current += value
        each_total.append(current)
        current = 0


    percents = []
    for each in each_total:
        percentage = int(each / total_spent * 100) // 10 * 10
        percents.append(percentage)
    final = ["Percentage spent by category"]
    for num in range (0, 101, 10)[::-1]:
        bar = "".join("o  " if p >= num else "   " for p in percents)
        if num == 0:
            final.append("  " + str(num) + "| " + bar)
        elif num < 100:
            final.append(" " + str(num) + "| " + bar)
        else:
            final.append(str(num) + "| " + bar)

    final.append("    -" + "---" * len(categories))
    names = [each.name for each in categories]
    length = max(len(name) for name in names)
    padded = [name.ljust(length) for name in names]
    for i in range(length):
        row = "".join([name[i].ljust(3) for name in padded])
        final.append("     " + row)
    return "\n".join(final)


groceries = Category("Groceries")
auto = Category("Auto")
water = Category("Water")

water.deposit(300, "Bill paid in advance")
water.withdraw(62, "water bill paid in full")
auto.deposit(672, description="Bank deposit")
auto.withdraw(259, description="car insurance")
groceries.deposit(925, description="Bank deposit")
groceries.deposit(150, description="Bank deposit")
groceries.withdraw(154, description="metric ton of bread")
groceries.withdraw(50, description="Avacados and bread for toast")
groceries.deposit(420, description="Bank deposit from savings")
auto.withdraw(221, description="Gas")
groceries.withdraw(175, description="truckload of bread")

print(create_spend_chart([groceries, auto, water]))
