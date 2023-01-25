from string import ascii_letters
from transliterate import translit


def ru_to_eng_slug(obj):
    for i in range(len(obj)):
        if obj[i] in ascii_letters:
            return obj
        else:
            translit(obj, reversed=True)
            return obj

