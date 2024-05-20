import typing

from pcapi.utils.clean_accents import clean_accents


NON_DIFFUSIBLE_TAG = "[ND]"

REGION_DEPARTMENT_CODES: dict[str, tuple[str, ...]] = {
    "Auvergne-Rhône-Alpes": ("01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"),
    "Bourgogne-Franche-Comté": ("21", "25", "39", "58", "70", "71", "89", "90"),
    "Bretagne": ("22", "29", "35", "56"),
    "Centre-Val de Loire": ("18", "28", "36", "37", "41", "45"),
    "Corse": ("2A", "2B", "20"),
    "Grand Est": ("08", "10", "51", "52", "54", "55", "57", "67", "68", "88"),
    "Hauts-de-France": ("02", "59", "60", "62", "80"),
    "Île-de-France": ("75", "77", "78", "91", "92", "93", "94", "95"),
    "Normandie": ("14", "27", "50", "61", "76"),
    "Nouvelle-Aquitaine": ("16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"),
    "Occitanie": ("09", "11", "12", "30", "31", "32", "34", "46", "48", "66", "65", "81", "82"),
    "Pays de la Loire": ("44", "49", "53", "72", "85"),
    "Provence-Alpes-Côte d'Azur": ("04", "05", "06", "13", "83", "84"),
    "Guadeloupe": ("971",),
    "Guyane": ("973",),
    "La Réunion": ("974",),
    "Martinique": ("972",),
    "Mayotte": ("976",),
    "Saint-Pierre-et-Miquelon": ("975",),
    "Wallis et Futuna": ("986",),
    "Polynésie Française": ("987",),
    "Nouvelle-Calédonie": ("988",),
}


def get_region_name_from_department(department: str | None) -> str:
    if department:
        for region, departments in REGION_DEPARTMENT_CODES.items():
            if department in departments:
                return region
    return "Aucune valeur"


def get_department_code_from_city_code(city_code: str) -> str:
    """city_code can be either the postalCode or the inseeCode.
    Trying to infer the departmentCode from the postalCode is
    STRONGLY DISCOURAGED as there is no link between the prefix
    of the postalCode and the departmentCode.
    Please always use inseeCode.
    """
    if city_code[:3] == "202":
        return "2B"

    if city_code[:2] == "20":
        return "2A"

    # Use a fake but distinguishable code for Monaco, used in
    # `core.educational.academis.ACADEMIES`.
    if city_code[:3] == "980":
        return "98"

    if city_code[:2] > "95":
        return city_code[:3]

    return city_code[:2]


def get_region_name_from_postal_code(postal_code: str) -> str:
    department_code = get_department_code_from_city_code(postal_code)
    region = get_region_name_from_department(department_code)
    return region


def get_all_regions() -> list[str]:
    # sort without accents to avoid "Île-de-France" at the end
    return sorted(REGION_DEPARTMENT_CODES.keys(), key=clean_accents)


def get_department_codes_for_region(region: str) -> tuple[str, ...]:
    return REGION_DEPARTMENT_CODES.get(region, ())


def get_department_codes_for_regions(regions: typing.Iterable[str]) -> tuple[str, ...]:
    return sum((get_department_codes_for_region(region) for region in regions), ())
