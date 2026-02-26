from pcapi.utils.regions import get_all_regions


def get_regions_choices() -> list[tuple]:
    return [(key, key) for key in get_all_regions()]
