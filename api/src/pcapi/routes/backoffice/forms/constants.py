from pcapi.utils.postal_code import DEPARTMENTS_NAMES


def _generate_area_choices_from_department_codes() -> list[tuple[str, str]]:
    areas = []
    for code, name in DEPARTMENTS_NAMES.items():
        if code == "20":
            # 20 in database, keep also 2A/2B in the label for autocomplete
            areas.append((code, f"{code} - {name} (2A/2B)"))
        else:
            areas.append((code, f"{code} - {name}"))
    return areas


# Departments and overseas collectivities
area_choices = tuple(_generate_area_choices_from_department_codes())
