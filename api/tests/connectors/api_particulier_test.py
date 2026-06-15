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

from tests.core.subscription.bonus.bonus_fixtures import AAH_ELIGIBLE_RESPONSE
from tests.core.subscription.bonus.bonus_fixtures import AEEH_ELIGIBLE_RESPONSE
from tests.core.subscription.bonus.bonus_fixtures import QUOTIENT_FAMILIAL_FIXTURE


class QuotientFamilialTest:
    def test_get_quotient_familial_for_french_household(self, requests_mock):
        custodian = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.M,
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
            "sexeEtatCivil": ["M"],
            "codeCogInseePaysNaissance": [countries_utils.FRANCE_INSEE_CODE],
            "codeCogInseeCommuneNaissance": ["08480"],
            "annee": ["2023"],
            "mois": ["6"],
        }

        assert quotient_familial_response == api_particulier.QuotientFamilialResponse(
            data=api_particulier.QuotientFamilialData(
                allocataires=[
                    api_particulier.ApiParticulierPerson(
                        nom_naissance="LEFEBVRE",
                        prenoms="ALEXIS GÉRÔME JEAN-PHILIPPE",
                        date_naissance=date(1982, 12, 27),
                        sexe=users_models.GenderEnum.M,
                    )
                ],
                enfants=[
                    api_particulier.ApiParticulierPerson(
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

    def test_get_quotient_familial_for_abroad_born_custodian_ignores_city_code(self, requests_mock):
        custodian = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code="99243",
            birth_city_cog_code="ignor",
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
            "sexeEtatCivil": ["M"],
            "codeCogInseePaysNaissance": ["99243"],
            "annee": ["2023"],
            "mois": ["6"],
        }
        assert "codeCogInseeCommuneNaissance" not in post_request.qs.keys()

    def test_get_quotient_familial_autofills_birth_country(self, requests_mock):
        custodian = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.F,
            birth_country_cog_code=None,
            birth_city_cog_code=None,
            birth_city=None,
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
            "codeCogInseePaysNaissance": [countries_utils.FRANCE_INSEE_CODE],
            "annee": ["2023"],
            "mois": ["6"],
        }

    @pytest.mark.parametrize(
        "status_code, exception",
        [
            (400, api_particulier.ParticulierApiQueryError),
            (404, api_particulier.ParticulierApiApplicationNotFound),
            (422, api_particulier.ParticulierApiPersonNotFound),
            (429, api_particulier.ParticulierApiRateLimitExceeded),
            (500, api_particulier.ParticulierApiUnavailable),
        ],
    )
    def test_quotient_familial_error(self, requests_mock, status_code, exception):
        custodian = subscription_factories.ApiParticulierPersonFactory.create()
        requests_mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=status_code, json={})

        with pytest.raises(exception):
            api_particulier.get_quotient_familial(custodian, date(2023, 6, 1))


class DisabledAdultAllowanceTest:
    def test_get_french_adult_disability_allowance(self, requests_mock):
        person = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="martin",
            common_name="dupont",
            first_names=["pierre", "richard"],
            birth_date=date(1987, 12, 1),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
            birth_city_cog_code="08480",
        )
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_ELIGIBLE_RESPONSE)

        disability_response = api_particulier.get_disabled_adult_allowance(person)

        post_request = requests_mock.last_request
        assert post_request.qs == {
            "recipient": [settings.PASS_CULTURE_SIRET],
            "nomNaissance": ["MARTIN"],
            "prenoms[]": ["PIERRE", "RICHARD"],
            "nomUsage": ["DUPONT"],
            "anneeDateNaissance": ["1987"],
            "moisDateNaissance": ["12"],
            "jourDateNaissance": ["1"],
            "sexeEtatCivil": ["M"],
            "codeCogInseePaysNaissance": ["99100"],
            "codeCogInseeCommuneNaissance": ["08480"],
        }

        assert disability_response == api_particulier.DisabledAdultAllowanceResponse(
            data=api_particulier.DisabledAdultAllowanceData(est_beneficiaire=True, date_debut_droit=date(2022, 11, 29))
        )

    def test_get_abroad_born_adult_disability_allowance_ignores_city_code(self, requests_mock):
        person = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code="99243",
            birth_city_cog_code="ignor",
        )
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_ELIGIBLE_RESPONSE)

        api_particulier.get_disabled_adult_allowance(person)

        post_request = requests_mock.last_request
        assert post_request.qs == {
            "recipient": [settings.PASS_CULTURE_SIRET],
            "nomNaissance": ["LEFEBVRE"],
            "prenoms[]": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
            "anneeDateNaissance": ["1982"],
            "moisDateNaissance": ["12"],
            "jourDateNaissance": ["27"],
            "sexeEtatCivil": ["M"],
            "codeCogInseePaysNaissance": ["99243"],
        }
        assert "codeCogInseeCommuneNaissance" not in post_request.qs.keys()

    def test_get_adult_disability_allowance_autofills_birth_country(self, requests_mock):
        person = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.F,
            birth_country_cog_code=None,
            birth_city_cog_code=None,
            birth_city=None,
        )
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_ELIGIBLE_RESPONSE)

        api_particulier.get_disabled_adult_allowance(person)

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
        }

    @pytest.mark.parametrize(
        "status_code, exception",
        [
            (400, api_particulier.ParticulierApiQueryError),
            (404, api_particulier.ParticulierApiApplicationNotFound),
            (422, api_particulier.ParticulierApiPersonNotFound),
            (429, api_particulier.ParticulierApiRateLimitExceeded),
            (500, api_particulier.ParticulierApiUnavailable),
        ],
    )
    def test_adult_disability_allowance_errors(self, requests_mock, status_code, exception):
        person = subscription_factories.ApiParticulierPersonFactory.create()
        requests_mock.get(api_particulier.AAH_ENDPOINT, status_code=status_code, json={})

        with pytest.raises(exception):
            api_particulier.get_disabled_adult_allowance(person)


class DisabledChildEducationAllowanceTest:
    def test_get_french_child_disability_allowance(self, requests_mock):
        person = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="dupont",
            first_names=["pierre"],
            birth_date=date(2015, 3, 12),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
            birth_city_cog_code="75112",
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=AEEH_ELIGIBLE_RESPONSE)

        disability_response = api_particulier.get_disabled_child_education_allowance(person)

        post_request = requests_mock.last_request
        assert post_request.qs == {
            "recipient": [settings.PASS_CULTURE_SIRET],
            "nomNaissance": ["DUPONT"],
            "prenoms[]": ["PIERRE"],
            "anneeDateNaissance": ["2015"],
            "moisDateNaissance": ["3"],
            "jourDateNaissance": ["12"],
            "sexeEtatCivil": ["M"],
            "codeCogInseePaysNaissance": ["99100"],
            "codeCogInseeCommuneNaissance": ["75112"],
        }

        assert disability_response == api_particulier.DisabledChildEducationAllowanceResponse(
            data=api_particulier.DisabledChildEducationAllowanceData(
                status=api_particulier.DisabledChildEducationAllowanceStatus.BENEFICIARY,
                date_debut_droit=date(2023, 6, 15),
            )
        )

    def test_get_abroad_born_disabled_child_education_allowance_ignores_city_code(self, requests_mock):
        person = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code="99243",
            birth_city_cog_code="ignor",
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=AEEH_ELIGIBLE_RESPONSE)

        api_particulier.get_disabled_child_education_allowance(person)

        post_request = requests_mock.last_request
        assert post_request.qs == {
            "recipient": [settings.PASS_CULTURE_SIRET],
            "nomNaissance": ["LEFEBVRE"],
            "prenoms[]": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
            "anneeDateNaissance": ["1982"],
            "moisDateNaissance": ["12"],
            "jourDateNaissance": ["27"],
            "sexeEtatCivil": ["M"],
            "codeCogInseePaysNaissance": ["99243"],
        }
        assert "codeCogInseeCommuneNaissance" not in post_request.qs.keys()

    def test_get_child_disability_allowance_autofills_birth_country(self, requests_mock):
        person = subscription_factories.ApiParticulierPersonFactory.create(
            last_name="dupont",
            first_names=["pierre"],
            birth_date=date(2015, 3, 12),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code=None,
            birth_city_cog_code=None,
            birth_city=None,
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=AEEH_ELIGIBLE_RESPONSE)

        api_particulier.get_disabled_child_education_allowance(person)

        post_request = requests_mock.last_request
        assert post_request.qs == {
            "recipient": [settings.PASS_CULTURE_SIRET],
            "nomNaissance": ["DUPONT"],
            "prenoms[]": ["PIERRE"],
            "anneeDateNaissance": ["2015"],
            "moisDateNaissance": ["3"],
            "jourDateNaissance": ["12"],
            "sexeEtatCivil": ["M"],
            "codeCogInseePaysNaissance": [countries_utils.FRANCE_INSEE_CODE],
        }

    @pytest.mark.parametrize(
        "status_code, exception",
        [
            (400, api_particulier.ParticulierApiQueryError),
            (404, api_particulier.ParticulierApiApplicationNotFound),
            (422, api_particulier.ParticulierApiPersonNotFound),
            (429, api_particulier.ParticulierApiRateLimitExceeded),
            (500, api_particulier.ParticulierApiUnavailable),
        ],
    )
    def test_adult_disability_allowance_errors(self, requests_mock, status_code, exception):
        person = subscription_factories.ApiParticulierPersonFactory.create()
        requests_mock.get(api_particulier.AEEH_ENDPOINT, status_code=status_code, json={})

        with pytest.raises(exception):
            api_particulier.get_disabled_child_education_allowance(person)
