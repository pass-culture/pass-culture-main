def get_occurrence_short_name(concatened_names_with_a_date):  # type: ignore [no-untyped-def]
    splitted_names = concatened_names_with_a_date.split(" / ")

    if len(splitted_names) > 0:
        return splitted_names[0]

    return None


def get_price_by_short_name(occurrence_short_name=None):  # type: ignore [no-untyped-def]
    if occurrence_short_name is None:
        return 0

    return sum(map(ord, occurrence_short_name)) % 50
