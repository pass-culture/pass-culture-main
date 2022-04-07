import unicodedata


def clean_accents(text: str):  # type: ignore [no-untyped-def]
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
