"""
Examples are taken from
https://github.com/etalab/siade_staging_data/tree/develop/payloads/api_particulier_v3_cnav_quotient_familial_with_civility
"""

import time
from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import timedelta
from email.utils import format_datetime

import pytest
from flask import current_app

from pcapi import settings
from pcapi.connectors import api_particulier
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription.bonus.constants import QUOTIENT_FAMILIAL_THRESHOLD
from pcapi.core.users import models as users_models
from pcapi.utils import countries as countries_utils

from tests.core.subscription.bonus.bonus_fixtures import AAH_RECIPIENT_RESPONSE
from tests.core.subscription.bonus.bonus_fixtures import AEEH_RECIPIENT_RESPONSE
from tests.core.subscription.bonus.bonus_fixtures import QUOTIENT_FAMILIAL_FIXTURE


class QuotientFamilialTest:
    def test_get_quotient_familial_for_french_household(self, requests_mock):
        custodian = subscription_factories.BonusCreditPersonFactory.create(
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
        custodian = subscription_factories.BonusCreditPersonFactory.create(
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
        assert "codeCogInseeCommuneNaissance" not in post_request.qs

    def test_get_quotient_familial_autofills_birth_country(self, requests_mock):
        custodian = subscription_factories.BonusCreditPersonFactory.create(
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
            (409, api_particulier.ParticulierApiRequestConflict),
            (422, api_particulier.ParticulierApiPersonNotFound),
            (429, api_particulier.ParticulierApiRateLimitExceeded),
            (500, api_particulier.ParticulierApiUnavailable),
        ],
    )
    def test_quotient_familial_error(self, requests_mock, status_code, exception):
        custodian = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=status_code, json={})

        with pytest.raises(exception):
            api_particulier.get_quotient_familial(custodian, date(2023, 6, 1))


class DisabledAdultAllowanceTest:
    def test_get_french_adult_disability_allowance(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create(
            last_name="martin",
            common_name="dupont",
            first_names=["pierre", "richard"],
            birth_date=date(1987, 12, 1),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
            birth_city_cog_code="08480",
        )
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_RECIPIENT_RESPONSE)

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
        person = subscription_factories.BonusCreditPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code="99243",
            birth_city_cog_code="ignor",
        )
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_RECIPIENT_RESPONSE)

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
        assert "codeCogInseeCommuneNaissance" not in post_request.qs

    def test_get_adult_disability_allowance_autofills_birth_country(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.F,
            birth_country_cog_code=None,
            birth_city_cog_code=None,
            birth_city=None,
        )
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_RECIPIENT_RESPONSE)

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
            (409, api_particulier.ParticulierApiRequestConflict),
            (422, api_particulier.ParticulierApiPersonNotFound),
            (429, api_particulier.ParticulierApiRateLimitExceeded),
            (500, api_particulier.ParticulierApiUnavailable),
        ],
    )
    def test_adult_disability_allowance_errors(self, requests_mock, status_code, exception):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(api_particulier.AAH_ENDPOINT, status_code=status_code, json={})

        with pytest.raises(exception):
            api_particulier.get_disabled_adult_allowance(person)


class DisabledChildEducationAllowanceTest:
    def test_get_french_child_disability_allowance(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create(
            last_name="dupont",
            first_names=["pierre"],
            birth_date=date(2015, 3, 12),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
            birth_city_cog_code="75112",
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=AEEH_RECIPIENT_RESPONSE)

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
                status=api_particulier.DisabledChildEducationAllowanceStatus.RECIPIENT,
                date_debut_droit=date(2023, 6, 15),
            )
        )

    def test_get_abroad_born_disabled_child_education_allowance_ignores_city_code(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create(
            last_name="lefebvre",
            common_name=None,
            first_names=["aleixs", "gréôme", "jean-philippe"],
            birth_date=date(1982, 12, 27),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code="99243",
            birth_city_cog_code="ignor",
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=AEEH_RECIPIENT_RESPONSE)

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
        assert "codeCogInseeCommuneNaissance" not in post_request.qs

    def test_get_child_disability_allowance_autofills_birth_country(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create(
            last_name="dupont",
            first_names=["pierre"],
            birth_date=date(2015, 3, 12),
            gender=users_models.GenderEnum.M,
            birth_country_cog_code=None,
            birth_city_cog_code=None,
            birth_city=None,
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=AEEH_RECIPIENT_RESPONSE)

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
            (409, api_particulier.ParticulierApiRequestConflict),
            (422, api_particulier.ParticulierApiPersonNotFound),
            (429, api_particulier.ParticulierApiRateLimitExceeded),
            (500, api_particulier.ParticulierApiUnavailable),
        ],
    )
    def test_adult_disability_allowance_errors(self, requests_mock, status_code, exception):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(api_particulier.AEEH_ENDPOINT, status_code=status_code, json={})

        with pytest.raises(exception):
            api_particulier.get_disabled_child_education_allowance(person)


class RateLimitTest:
    def _get_rate_limit_key(self) -> str:
        time_window_id = int(time.time()) // api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE
        return (
            f"pcapi:rate_limit:{api_particulier.RATE_LIMIT_KEY}"
            f":{api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE}:{time_window_id}"
        )

    def test_retry_after_in_seconds(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(
            api_particulier.AAH_ENDPOINT,
            status_code=429,
            json={},
            headers={
                "RateLimit-Limit": "200",
                "RateLimit-Remaining": "0",
                "RateLimit-Reset": "37",
                "Retry-After": "37",
            },
        )

        with pytest.raises(api_particulier.ParticulierApiRateLimitExceeded) as error:
            api_particulier.get_disabled_adult_allowance(person)

        assert error.value.retry_after == 37

    def test_retry_after_as_http_date(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create()
        in_one_minute = datetime.now(UTC) + timedelta(minutes=1)
        requests_mock.get(
            api_particulier.AAH_ENDPOINT,
            status_code=429,
            json={},
            headers={"Retry-After": format_datetime(in_one_minute, usegmt=True)},
        )

        with pytest.raises(api_particulier.ParticulierApiRateLimitExceeded) as error:
            api_particulier.get_disabled_adult_allowance(person)

        assert 50 <= error.value.retry_after <= 60

    def test_retry_after_falls_back_on_rate_limit_reset(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(
            api_particulier.AEEH_ENDPOINT,
            status_code=429,
            json={},
            headers={"RateLimit-Limit": "200", "RateLimit-Remaining": "0", "RateLimit-Reset": "12"},
        )

        with pytest.raises(api_particulier.ParticulierApiRateLimitExceeded) as error:
            api_particulier.get_disabled_child_education_allowance(person)

        assert error.value.retry_after == 12

    def test_no_retry_after_when_the_api_does_not_send_any(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(api_particulier.AAH_ENDPOINT, status_code=500, json={})

        with pytest.raises(api_particulier.ParticulierApiUnavailable) as error:
            api_particulier.get_disabled_adult_allowance(person)

        assert error.value.retry_after is None

    def test_further_calls_fail_early_until_retry_after_passes(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(api_particulier.AAH_ENDPOINT, status_code=429, json={}, headers={"Retry-After": "37"})
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=AEEH_RECIPIENT_RESPONSE)

        with pytest.raises(api_particulier.ParticulierApiRateLimitExceeded):
            api_particulier.get_disabled_adult_allowance(person)

        # any endpoint, not only the one that got rate limited
        with pytest.raises(api_particulier.ParticulierApiRateLimitExceeded) as error:
            api_particulier.get_disabled_child_education_allowance(person)

        assert requests_mock.call_count == 1
        assert error.value.retry_after == 37
        assert current_app.redis_client.ttl(api_particulier.RATE_LIMIT_LOCK_KEY) == 37

    def test_locked_calls_do_not_consume_the_client_side_rate_limit(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_RECIPIENT_RESPONSE)
        current_app.redis_client.set(api_particulier.RATE_LIMIT_LOCK_KEY, "1", ex=60)

        with pytest.raises(api_particulier.ParticulierApiRateLimitExceeded):
            api_particulier.get_disabled_adult_allowance(person)

        assert not requests_mock.called
        assert current_app.redis_client.get(self._get_rate_limit_key()) is None

    def test_client_side_rate_limit_does_not_call_the_api(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_RECIPIENT_RESPONSE)
        current_app.redis_client.set(self._get_rate_limit_key(), settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD)

        with pytest.raises(api_particulier.ParticulierApiRateLimitExceeded) as error:
            api_particulier.get_disabled_adult_allowance(person)

        assert not requests_mock.called
        assert 0 < error.value.retry_after <= api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE

    def test_calls_are_counted_in_the_client_side_rate_limit(self, requests_mock):
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=AAH_RECIPIENT_RESPONSE)

        api_particulier.get_disabled_adult_allowance(person)

        assert int(current_app.redis_client.get(self._get_rate_limit_key())) == 1
