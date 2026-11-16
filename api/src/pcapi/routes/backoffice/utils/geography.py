from wtforms import fields as wtforms_fields

from pcapi.utils.regions import get_all_regions


def get_regions_choices() -> list[wtforms_fields.SelectChoice]:
    return [wtforms_fields.SelectChoice(key, key) for key in get_all_regions()]
