import random

with open("poetry_lines.csv") as f:
    poetry_lines = f.readlines()
quadruplets = []
piece = []
piece2 = []
piece3 = []
piece4 = []
count = 0

for line in poetry_lines:
    count += 1

    for word in line.split():
        if count == 1:
            piece.append(word.replace(".", "").lower())
        elif count == 2:
            piece.append(word.replace(".", "").lower())
            piece2.append(word.replace(".", "").lower())
        elif count == 3:
            piece.append(word.replace(".", "").lower())
            piece2.append(word.replace(".", "").lower())
            piece3.append(word.replace(".", "").lower())
        else:
            piece.append(word.replace(".", "").lower())
            piece2.append(word.replace(".", "").lower())
            piece3.append(word.replace(".", "").lower())
            piece4.append(word.replace(".", "").lower())

        if len(piece) == 4:
            quadruplets.append(piece)
            piece = []
        elif len(piece2) == 4:
            quadruplets.append(piece2)
            piece2 = []
        elif len(piece3) == 4:
            quadruplets.append(piece3)
            piece3 = []
        elif len(piece4) == 4:
            quadruplets.append(piece4)
            piece4 = []

word = "the"
quads = []
final = ""

def appending_quadruplets(word):
    for quad in quadruplets:
        if quad[0].lower() == word.lower():
            quads.append(quad)

for _ in range(6):
    try:
        if _ == 0:
            appending_quadruplets(word)
            the_choice = random.choice(quads)
            final += " ".join(the_choice)
            quads = []
            word = the_choice[3]
        else:
            appending_quadruplets(word)
            the_choice = random.choice(quads)
            final += " ".join(the_choice[1:])
            quads = []
            word = the_choice[3]
        final += " "
    except IndexError:
        break


print(final.capitalize().strip() + ".")