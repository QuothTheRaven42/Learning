# def square_sum(numbers: list):
#     return sum(number*number for number in numbers)
#
# print(square_sum([0, 3, 4, 5]))

# def find_it(seq):
#     count = {x: seq.count(x) for x in set(seq)}
#     item = count.popitem()
#     print(item)
#     if item[1] % 2 == 1:
#         return item[0]
#     else:
#         return count.popitem()[0]
#
# print(find_it([10, 11, 13, 11, 3, 3, 3, 3, 3, 13]))

# def descending_order(num: int):
#     sorted_nums = sorted(str(num))
#     return "".join(sorted_nums[::-1])
#
# print(descending_order(123567894))

# def lovefunc(flower1, flower2):
#     if flower1 % 2 == 0 and flower2 % 2 == 1:
#         return True
#     else flower1 % 2 == 1 and flower2 % 2 == 0:
#         return True
#     Return False

# def lovefunc(flower1, flower2):
#     if flower1 % 2 == 0 and flower2 % 2 == 1: return True
#     if flower1 % 2 == 1 and flower2 % 2 == 0: return True
#     return False
#
# print(lovefunc(1, 4))
# print(lovefunc(2, 2))
# print(lovefunc(0, 1))
# print(lovefunc(0, 0))

# def fizzbuzz(num: int) -> list:
#     final = []
#     for each in range(1,num+1):
#          if each % 15 == 0:
#              final.append("FizzBuzz")
#          elif each % 3 == 0:
#              final.append("Fizz")
#          elif each % 5 == 0:
#              final.append("Buzz")
#          else: final.append(str(each))
#
#     return final
#
# print(fizzbuzz(15))

# '''
# find_user("Colt", "Steele") # 1
# find_user("Alan", "Turing") # 3
# find_user("Not", "Here") # 'Not Here not found.'
# '''
# from csv import reader
#
# def find_user(first, last):
#     with open("users.csv") as f:
#         csv_reader = reader(f)
#         index = 0
#         for row in csv_reader:
#             if row[0] == first and row[1] == last:
#                 return index
#             index += 1
#         return f"{first} {last} not found."
#
#
# print(find_user("Colt", "Steele")) # 1
# print(find_user("Alan", "Turing")) # 3
# print(find_user("Not", "Here")) # Not Found.

# def DNA_strand(dna):
#     chars = list(dna)
#     new_chars = ''
#     for char in chars:
#         if char == 'A': new_chars += 'T'
#         elif char == 'T': new_chars += 'A'
#         elif char == 'C': new_chars += 'G'
#         elif char == 'G': new_chars += 'C'
#     return new_chars
#
# print(DNA_strand("ATTGC"))

# def reverse_words(text):
#     return ' '.join(text[::-1].split(' ')[::-1])
#
# print(reverse_words('  double  spaced  words  '))


# import csv
#
# def update_users(old_first, old_last, new_first, new_last):
#     updated_count = 0
#     rows = []
#     with open('users.csv', 'r') as f:
#         reader = csv.reader(f)
#         for row in reader:
#             rows.append(row)
#
#     for row in rows:
#         if row[0] == old_first and row[1] == old_last:
#             row[0] = new_first
#             row[1] = new_last
#             updated_count += 1
#
#     with open('users.csv', 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)
#
#     return f"Users updated: {updated_count}."
#
# import csv
#
# def delete_users(first, last):
#     rows = []
#
#     with open('users.csv', 'r') as f:
#         reader = csv.reader(f)
#         for row in reader:
#             rows.append(row)
#
#     new_rows = [row for row in rows if not (row[0] == first and row[1] == last)]
#     updated_count = len(rows) - len(new_rows)
#
#     with open('users.csv', 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerows(new_rows)
#
#     return f"Users deleted: {updated_count}."

