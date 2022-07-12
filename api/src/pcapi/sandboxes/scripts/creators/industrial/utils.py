from decimal import Decimal


def get_occurrence_short_name_or_none(concatened_names_with_a_date: str) -> str | None:
    splitted_names = concatened_names_with_a_date.split(" / ")

    if len(splitted_names) > 0:
        return splitted_names[0]

    return None


def get_occurrence_short_name(concatened_names_with_a_date: str) -> str:
    short_name = get_occurrence_short_name_or_none(concatened_names_with_a_date)
    if not short_name:
        raise ValueError("Missing value from short name, please verify how shortname is build")

    return short_name


def get_price_by_short_name(occurrence_short_name: str = None) -> Decimal:
    if occurrence_short_name is None:
        return Decimal(0)

    return Decimal(str(sum(map(ord, occurrence_short_name)) % 50))
