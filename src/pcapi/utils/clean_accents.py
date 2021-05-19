import unicodedata


def clean_accents(text: str):
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
