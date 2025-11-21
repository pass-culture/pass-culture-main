import datetime

import pytest
import requests_mock

import pcapi.connectors.api_particulier as api_particulier
import pcapi.core.subscription.bonus.api as bonus_api
import pcapi.core.subscription.bonus.schemas as bonus_schemas
import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
import pcapi.utils.transaction_manager as transaction_manager

import tests.core.subscription.bonus.bonus_fixtures as bonus_fixtures


@pytest.mark.usefixtures("db_session")
class GetQuotientFamilialTest:
    def test_apply_for_quotient_familial_bonus(self):
        user = users_factories.BeneficiaryFactory()
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

            with transaction_manager.atomic():
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

            with transaction_manager.atomic():
                bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_NOT_FOUND]
        assert bonus_fraud_check.source_data().quotient_familial is None
