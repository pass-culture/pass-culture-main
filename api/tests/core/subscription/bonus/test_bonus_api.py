import copy
import datetime
import decimal

import pytest
import requests_mock

import pcapi.connectors.api_particulier as api_particulier
import pcapi.core.finance.models as finance_models
import pcapi.core.subscription.bonus.api as bonus_api
import pcapi.core.subscription.bonus.schemas as bonus_schemas
import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models

import tests.core.subscription.bonus.bonus_fixtures as bonus_fixtures


@pytest.mark.usefixtures("db_session")
class GetQuotientFamilialTest:
    def test_apply_for_quotient_familial_bonus(self):
        child_data = bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE["data"]["enfants"][0]
        last_name = child_data["nom_naissance"]
        first_names = child_data["prenoms"]
        birth_date = datetime.date.fromisoformat(child_data["date_naissance"])
        user = users_factories.BeneficiaryFactory(
            lastName=last_name, firstName=first_names, validatedBirthDate=birth_date
        )
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent={
                "custodian": {
                    "last_name": "LEFEBVRE",
                    "first_names": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
                    "birth_date": datetime.date(1982, 12, 27),
                    "gender": users_models.GenderEnum.F.value,
                    "birth_country_cog_code": "99243",
                    "birth_city_cog_code": "08480",
                },
                "quotient_familial": None,
            },
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert bonus_fraud_check.source_data() == bonus_schemas.QuotientFamilialBonusCreditContent(
            custodian=bonus_schemas.QuotientFamilialCustodian(
                last_name="LEFEBVRE",
                common_name=None,
                first_names=["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
                birth_date=datetime.date(1982, 12, 27),
                gender=users_models.GenderEnum.F,
                birth_country_cog_code="99243",
                birth_city_cog_code="08480",
            ),
            quotient_familial=bonus_schemas.QuotientFamilialContent(
                provider="CNAF", value=2550, year=2023, month=6, computation_year=2024, computation_month=12
            ),
        )
        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_minimum_quotient_familial_retained(self):
        child_data = bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE["data"]["enfants"][0]
        birth_date = datetime.date.fromisoformat(child_data["date_naissance"])
        user = users_factories.BeneficiaryFactory(
            lastName=child_data["nom_naissance"], firstName=child_data["prenoms"], validatedBirthDate=birth_date
        )
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        high_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        high_quotient_familial["data"]["quotient_familial"]["valeur"] = 9_999_999

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=high_quotient_familial)
            mock.get(
                f"{api_particulier.QUOTIENT_FAMILIAL_ENDPOINT}?mois={birth_date.month}",
                json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE,
            )

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert (
            bonus_fraud_check.source_data().quotient_familial.value
            == bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE["data"]["quotient_familial"]["valeur"]
        )
        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        assert user.recreditAmountToShow == decimal.Decimal("30")

    def test_custodian_not_found(self):
        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=404)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.CUSTODIAN_NOT_FOUND]
        assert bonus_fraud_check.source_data().quotient_familial is None
        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_user_not_in_tax_household(self):
        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]
        assert bonus_fraud_check.source_data().quotient_familial is None
        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_user_quotient_familial_too_high(self):
        child_data = bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE["data"]["enfants"][0]
        last_name = child_data["nom_naissance"]
        first_names = child_data["prenoms"]
        birth_date = datetime.date.fromisoformat(child_data["date_naissance"])
        user = users_factories.BeneficiaryFactory(
            lastName=last_name, firstName=first_names, validatedBirthDate=birth_date
        )
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        high_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        high_quotient_familial["data"]["quotient_familial"]["valeur"] = 9_999_999

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=high_quotient_familial)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH]
        assert bonus_fraud_check.source_data().quotient_familial == bonus_schemas.QuotientFamilialContent(
            provider="CNAF", value=9_999_999, year=2023, month=6, computation_year=2024, computation_month=12
        )
        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
