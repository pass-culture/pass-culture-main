def trim_with_elipsis(string: str, length: int) -> str:
    length_wo_elipsis = length - 1
    return string[:length_wo_elipsis] + (string[length_wo_elipsis:] and "…")
