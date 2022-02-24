import unicodedata


def is_latin(s: str) -> bool:
    if s == "":
        return False
    for char in s:
        if char in (" ", "-", ".", ",", "'", "’"):
            continue
        try:
            if not "LATIN" in unicodedata.name(char):
                return False
        # if unicodedata.name does not recognize char, it raises a ValueError
        except ValueError:
            return False
    return True


def has_latin_or_numeric_chars(address: str) -> bool:
    for char in address:
        if char == " ":
            continue
        if not is_latin(char) and not char.isnumeric():
            return False
    return True
