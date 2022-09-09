import typing

from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.backoffice.serialization import PaginatedResponse
from pcapi.routes.serialization import BaseModel


REGION_DEPARTMENT_CODES = {
    "Auvergne-Rhône-Alpes": ("01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"),
    "Bourgogne-Franche-Comté": ("21", "25", "39", "58", "70", "71", "89", "90"),
    "Bretagne": ("22", "29", "35", "56"),
    "Centre-Val de Loire": ("18", "28", "36", "37", "41", "45"),
    "Corse": ("2A", "2B"),
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


def get_department_code_from_postal_code(postal_code: str) -> str:
    if int(postal_code[:3]) == 202:
        return "2B"

    if int(postal_code[:2]) == 20:
        return "2A"

    if int(postal_code[:2]) > 95:
        return postal_code[:3]

    return postal_code[:2]


def get_region_name_from_postal_code(postal_code: str) -> str:
    department_code = get_department_code_from_postal_code(postal_code)
    for region, departments in REGION_DEPARTMENT_CODES.items():
        if department_code in departments:
            return region

    return "inconnue"


def get_user_or_error(user_id: int, error_code: int = 400) -> users_models.User:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "L'utilisateur n'existe pas"}, status_code=error_code)

    return user


def build_paginated_response(
    page: int,
    pages: int,
    total: int,
    sort: str | None,
    data: list[BaseModel],
    response_model: typing.Type[PaginatedResponse] = PaginatedResponse,
) -> PaginatedResponse:
    response = response_model(pages=pages, total=total, page=page, size=len(data), sort=sort, data=data)
    return response
