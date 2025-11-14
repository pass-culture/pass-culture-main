"""
Examples are taken from
https://github.com/etalab/siade_staging_data/tree/develop/payloads/api_particulier_v3_cnav_quotient_familial_with_civility
"""

from datetime import date

import pytest

from pcapi import settings
from pcapi.connectors import api_particulier
from pcapi.core.users import models as users_models


QUOTIENT_FAMILIAL_FIXTURE = {
    "data": {
        "allocataires": [
            {
                "nom_naissance": "LEFEBVRE",
                "nom_usage": None,
                "prenoms": "ALEXIS GÉRÔME JEAN-PHILIPPE",
                "date_naissance": "1982-12-27",
                "sexe": "F",
            }
        ],
        "enfants": [
            {
                "nom_naissance": "LEFEBVRE",
                "nom_usage": None,
                "prenoms": "LEO",
                "date_naissance": "1990-04-20",
                "sexe": "M",
            }
        ],
        "adresse": {
            "destinataire": "Monsieur LEFEBVRE ALEXIS GÉRÔME JEAN-PHILIPPE",
            "complement_information": None,
            "complement_information_geographique": None,
            "numero_libelle_voie": "1 RUE MONTORGUEIL",
            "lieu_dit": None,
            "code_postal_ville": "75002 PARIS",
            "pays": "FRANCE",
        },
        "quotient_familial": {
            "fournisseur": "CNAF",
            "valeur": 2550,
            "annee": 2023,
            "mois": 6,
            "annee_calcul": 2024,
            "mois_calcul": 12,
        },
    },
    "links": {},
    "meta": {},
}


@pytest.mark.usefixtures("db_session")
def test_get_quotient_familial_for_french_household(requests_mock):
    requests_mock.get(
        api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
        json=QUOTIENT_FAMILIAL_FIXTURE,
    )

    quotient_familial_response = api_particulier.get_quotient_familial(
        last_name="lefebvre",
        first_names=["aleixs", "gréôme", "jean-philippe"],
        birth_date=date(1982, 12, 27),
        gender=users_models.GenderEnum.F,
        country_insee_code="99100",
        city_insee_code="08480",
        quotient_familial_date=date(2023, 6, 1),
    )

    post_request = requests_mock.last_request
    assert post_request.qs == {
        "recipient": [settings.PASS_CULTURE_SIRET],
        "nomNaissance": ["LEFEBVRE"],
        "prenoms[]": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
        "anneeDateNaissance": ["1982"],
        "moisDateNaissance": ["12"],
        "jourDateNaissance": ["27"],
        "sexeEtatCivil": ["F"],
        "codeCogInseePaysNaissance": [api_particulier.FRANCE_INSEE_CODE],
        "codeCogInseeCommuneNaissance": ["08480"],
        "annee": ["2023"],
        "mois": ["6"],
    }

    assert quotient_familial_response == api_particulier.QuotientFamilialResponse(
        data=api_particulier.QuotientFamilialData(
            allocataires=[
                api_particulier.QuotientFamilialPerson(
                    nom_naissance="LEFEBVRE",
                    prenoms="ALEXIS GÉRÔME JEAN-PHILIPPE",
                    date_naissance=date(1982, 12, 27),
                    sexe=users_models.GenderEnum.F,
                )
            ],
            enfants=[
                api_particulier.QuotientFamilialPerson(
                    nom_naissance="LEFEBVRE",
                    prenoms="LEO",
                    date_naissance=date(1990, 4, 20),
                    sexe=users_models.GenderEnum.M,
                )
            ],
            quotient_familial=api_particulier.QuotientFamilial(
                fournisseur="CNAF",
                valeur=2550,
                annee=2023,
                mois=6,
                annee_calcul=2024,
                mois_calcul=12,
            ),
        )
    )


def test_get_quotient_familial_for_french_born_custodian_without_city_code(requests_mock):
    requests_mock.get(
        api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
        json=QUOTIENT_FAMILIAL_FIXTURE,
    )

    with pytest.raises(ValueError) as exception:
        api_particulier.get_quotient_familial(
            last_name="lefebvre",
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.F,
            country_insee_code=api_particulier.FRANCE_INSEE_CODE,
            city_insee_code=None,
            quotient_familial_date=date(2023, 6, 1),
        )

        assert "City INSEE code is mandatory when the custodian is born in France" in str(exception)


def test_get_quotient_familial_for_abroad_born_custodian_ignores_city_code(requests_mock):
    requests_mock.get(
        api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
        json=QUOTIENT_FAMILIAL_FIXTURE,
    )

    api_particulier.get_quotient_familial(
        last_name="lefebvre",
        first_names=["aleixs", "gréôme", "jean-philippe"],
        birth_date=date(1982, 12, 27),
        gender=users_models.GenderEnum.F,
        country_insee_code="99243",
        city_insee_code="ignore me",
        quotient_familial_date=date(2023, 6, 1),
    )

    post_request = requests_mock.last_request
    assert post_request.qs == {
        "recipient": [settings.PASS_CULTURE_SIRET],
        "nomNaissance": ["LEFEBVRE"],
        "prenoms[]": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
        "anneeDateNaissance": ["1982"],
        "moisDateNaissance": ["12"],
        "jourDateNaissance": ["27"],
        "sexeEtatCivil": ["F"],
        "codeCogInseePaysNaissance": ["99243"],
        "annee": ["2023"],
        "mois": ["6"],
    }
    assert "codeCogInseeCommuneNaissance" not in post_request.qs.keys()


@pytest.mark.parametrize(
    "status_code, exception",
    [
        (400, api_particulier.ParticulierApiQueryError),
        (429, api_particulier.ParticulierApiRateLimitExceeded),
        (500, api_particulier.ParticulierApiUnavailable),
    ],
)
def test_quotient_familial_error(requests_mock, status_code, exception):
    requests_mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=status_code)

    with pytest.raises(exception):
        api_particulier.get_quotient_familial(
            last_name="lefebvre",
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.F,
            country_insee_code="99100",
            city_insee_code="08480",
            quotient_familial_date=date(2023, 6, 1),
        )
