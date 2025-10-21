from datetime import date

from pydantic import BaseModel
from pydantic import field_validator

from pcapi import settings
from pcapi.core.users import models as users_models
from pcapi.utils import requests


QUOTIENT_FAMILIAL_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/quotient_familial/identite"

FRANCE_INSEE_CODE = "99100"


class QuotientFamilialPerson(BaseModel):
    nom_naissance: str
    nom_usage: str | None = None
    prenoms: str
    date_naissance: date
    sexe: users_models.GenderEnum

    @field_validator("sexe", mode="before")
    @classmethod
    def parse_gender(cls, gender: str | users_models.GenderEnum) -> users_models.GenderEnum:
        if isinstance(gender, str):
            return users_models.GenderEnum[gender]
        return gender


class QuotientFamilial(BaseModel):
    fournisseur: str
    valeur: int
    annee: int
    mois: int
    annee_calcul: int
    mois_calcul: int


class QuotientFamilialData(BaseModel):
    allocataires: list[QuotientFamilialPerson]
    enfants: list[QuotientFamilialPerson]
    quotient_familial: QuotientFamilial


class QuotientFamilialResponse(BaseModel):
    data: QuotientFamilialData


def get_quotient_familial(
    last_name: str,
    first_names: list[str],
    birth_date: date,
    gender: users_models.GenderEnum,
    country_insee_code: str,
    city_insee_code: str | None,
    quotient_familial_date: date,
) -> QuotientFamilialResponse:
    """
    Get the Quotient Familial from a tax household, using a custodian name.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Quotient-familial-CAF-and-MSA
    """

    if country_insee_code == FRANCE_INSEE_CODE and not city_insee_code:
        raise ValueError("City INSEE code is mandatory when the custodian is born in France")

    if country_insee_code != FRANCE_INSEE_CODE:
        city_insee_code = None

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in first_names],
        "anneeDateNaissance": birth_date.year,
        "moisDateNaissance": birth_date.month,
        "jourDateNaissance": birth_date.day,
        "sexeEtatCivil": gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
        "annee": quotient_familial_date.year,
        "mois": quotient_familial_date.month,
    }
    response = requests.get(
        QUOTIENT_FAMILIAL_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
    )
    response.raise_for_status()

    quotient_familial = QuotientFamilialResponse.model_validate(response.json())
    return quotient_familial
