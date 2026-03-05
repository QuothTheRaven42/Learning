
# print(file.readlines())
# file.close()
# print(file.closed)

# with open('story.txt', 'w') as file:
#     file.write('Writing to a file.\n')
#     file.write('This is another line.\n')
#     file.write('We have reached the end.\n')

# with open('lol.txt', 'r+') as file:
#     text = file.read()
#     print(len(text))

# def statistics(filename):
#     counts = {}
#
#     with open(filename, 'r') as file:
#         text = file.read()
#
#         counts['characters'] = len(text)
#         file.seek(0)
#
#         all_words = text.split()
#         counts['words'] = len(all_words)
#         file.seek(0)
#
#         counts['lines'] = len(file.readlines())
#     return counts
#
# print(statistics('story.txt'))


def find_and_replace(filename, words, replacement):
    with open(filename, 'r+') as file:
        text = file.read()
        return text.replace(words, replacement)

print(find_and_replace('story.txt', 'text', 'words'))



