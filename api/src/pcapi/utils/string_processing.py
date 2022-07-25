import re


def trim_with_elipsis(string: str, length: int) -> str:
    length_wo_elipsis = length - 1
    return string[:length_wo_elipsis] + (string[length_wo_elipsis:] and "…")


def tokenize_for_search(string: str) -> list[str]:
    return re.split("[^0-9a-zÀ-ÿ]+", string.lower())


def remove_single_letters_for_search(keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if len(keyword) > 1]
