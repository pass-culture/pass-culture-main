import re


def trim_with_elipsis(string, length):
    length_wo_elipsis = length - 1
    return string[:length_wo_elipsis] + (string[length_wo_elipsis:] and "…")


def tokenize_for_search(string):
    return re.split("[^0-9a-zÀ-ÿ]+", string.lower())


def remove_single_letters_for_search(array_of_keywords):
    return list(filter(lambda k: len(k) > 1, array_of_keywords))
