"""More file IO, Reading CSV files, pickling"""

# THIS DOES READ THE FILE BUT IT DOESN'T PARSE IT!
# BAD!!!!!!
# with open("fighters.csv") as file:
#     data = file.read()
#     print(data)

# Using reader
# from csv import reader

# with open("fighters.csv") as file:
#     csv_reader = reader(file) # iterator, not list
#     data = list(csv_reader) # Example where data is cast into a list
    # print(csv_reader) # csv.reader object
    # print(data)
    # next(csv_reader)
    # for fighter in csv_reader:
        # print(f"{fighter[0]}: {fighter[1]}")

# Reading/Parsing CSV Using a DictReader:
# from csv import DictReader
#
# with open("fighters.csv") as file:
#     csv_reader = DictReader(file)
#     for row in csv_reader:
        # each row is an OrderedDict
        # print(row['Name'])

# writing to CSV with lists
# from csv import writer, reader
#
#
# with open("fighters.csv") as file:
#     csv_reader = reader(file)
#     # fighters = [[s.upper() for s in row] for row in csv_reader]
#     with open("screaming_fighters.csv", "w") as file:
#         csv_writer = writer(file)
#         for fighter in csv_reader:
#             csv_writer.writerow([s.upper() for s in fighter])

#
# from csv import DictWriter
# #
# with open("cat.csv", "w") as file:
#     headers = ["Name", "Breed", "Age"]
#     csv_writer = DictWriter(file, fieldnames=headers)
#     csv_writer.writeheader()
#     csv_writer.writerow({
#         "Name": "Lucifer",
#         "Breed": "Blacksmoke",
#         "Age": "7"
#     })

# from csv import DictReader, DictWriter
#
# def cm_to_in(cm):
#     return int(cm) * 0.393701
#
# with open('fighters (1).csv') as file:
#     csv_reader = DictReader(file)
#     fighters = list(csv_reader)
#
# with open("inches_fighters.csv", "w") as file:
#     headers = ("Name", "Country", "Height")
#     csv_writer = DictWriter(file, fieldnames=headers)
#     csv_writer.writeheader()
#     for fighter in fighters:
#         csv_writer.writerow({
#             "Name": fighter["Name"],
#             "Country": fighter["Country"],
#             "Height": round(cm_to_in(fighter["Height (in cm)"]), 2)
#         })

# import csv
#
# def add_cat(name, breed, age):
#     filename = 'cat.csv'
#     with open(filename, "a") as file:
#         writer = csv.writer(file)
#         writer.writerow([name,breed,age])
#
# add_cat("Daisy","Calico", "8")
# add_cat("Blue","Russian Blue", "3")



'''
find_user("Colt", "Steele") # 1
find_user("Alan", "Turing") # 3
find_user("Not", "Here") # 'Not Here not found.'
'''
from csv import reader

def find_user(first, last):
    with open("users.csv") as f:
        csv_reader = reader(f)
        index = 0
        for row in csv_reader:
            if row[0] == first and row[1] == last:
                return index
            index += 1
        return f"{first} {last} not found."


print(find_user("Colt", "Steele")) # 1
print(find_user("Alan", "Turing")) # 3
print(find_user("Not", "Here")) # Not Found.