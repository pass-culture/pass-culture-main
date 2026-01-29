"""
Examples are taken from
https://github.com/etalab/siade_staging_data/tree/develop/payloads/api_particulier_v3_cnav_quotient_familial_with_civility
"""

from datetime import date

import pytest

from pcapi import settings
from pcapi.connectors import api_particulier
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription.bonus.constants import QUOTIENT_FAMILIAL_THRESHOLD
from pcapi.core.users import models as users_models
from pcapi.utils import countries as countries_utils

from tests.core.subscription.bonus.bonus_fixtures import QUOTIENT_FAMILIAL_FIXTURE


def test_get_quotient_familial_for_french_household(requests_mock):
    custodian = subscription_factories.QuotientFamilialCustodianFactory.create(
        last_name="lefebvre",
        common_name=None,
        first_names=["aleixs", "gréôme", "jean-philippe"],
        birth_date=date(1982, 12, 27),
        gender=users_models.GenderEnum.F,
        birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
        birth_city_cog_code="08480",
    )
    requests_mock.get(
        api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
        json=QUOTIENT_FAMILIAL_FIXTURE,
    )

    quotient_familial_response = api_particulier.get_quotient_familial(custodian, date(2023, 6, 1))

    post_request = requests_mock.last_request
    assert post_request.qs == {
        "recipient": [settings.PASS_CULTURE_SIRET],
        "nomNaissance": ["LEFEBVRE"],
        "prenoms[]": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
        "anneeDateNaissance": ["1982"],
        "moisDateNaissance": ["12"],
        "jourDateNaissance": ["27"],
        "sexeEtatCivil": ["F"],
        "codeCogInseePaysNaissance": [countries_utils.FRANCE_INSEE_CODE],
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
                valeur=QUOTIENT_FAMILIAL_THRESHOLD,
                annee=2023,
                mois=6,
                annee_calcul=2024,
                mois_calcul=12,
            ),
        )
    )


def test_get_quotient_familial_for_french_born_custodian_without_city_code(requests_mock):
    custodian = subscription_factories.QuotientFamilialCustodianFactory.create(
        birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE, birth_city_cog_code=""
    )
    requests_mock.get(
        api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
        json=QUOTIENT_FAMILIAL_FIXTURE,
    )

    with pytest.raises(ValueError) as exception:
        api_particulier.get_quotient_familial(custodian, date(2023, 6, 1))

        assert "City INSEE code is mandatory when the custodian is born in France" in str(exception)


def test_get_quotient_familial_for_abroad_born_custodian_ignores_city_code(requests_mock):
    custodian = subscription_factories.QuotientFamilialCustodianFactory.create(
        last_name="lefebvre",
        common_name=None,
        first_names=["aleixs", "gréôme", "jean-philippe"],
        birth_date=date(1982, 12, 27),
        gender=users_models.GenderEnum.F,
        birth_country_cog_code="99243",
        birth_city_cog_code="ignore me",
    )
    requests_mock.get(
        api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
        json=QUOTIENT_FAMILIAL_FIXTURE,
    )

    api_particulier.get_quotient_familial(custodian, date(2023, 6, 1))

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
    custodian = subscription_factories.QuotientFamilialCustodianFactory.create()
    requests_mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=status_code)

    with pytest.raises(exception):
        api_particulier.get_quotient_familial(custodian, date(2023, 6, 1))
