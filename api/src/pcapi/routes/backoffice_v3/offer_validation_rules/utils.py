import unicodedata


def convert_to_unaccent_lowercase(input_string: str) -> str:
    nfkd_form = unicodedata.normalize("NFKD", input_string)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()
