import pytest

from pcapi.connectors import api_particulier
from pcapi.core.finance import models as finance_models
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import api as bonus_api
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models

from tests.core.subscription.bonus import bonus_fixtures


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(ENABLE_PARTICULIER_API_MOCK=True)
class StagingQuotientFamilialTest:
    def test_mock_eligible_quotient_familial(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        config_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                http_status_code=200,
                quotient_familial=bonus_schemas.QuotientFamilialContent(
                    provider="CNAF", value=123, year=2023, month=6, computation_year=2024, computation_month=12
                ),
                children=[
                    bonus_schemas.QuotientFamilialChild(
                        last_name=user.lastName,
                        common_name=None,
                        first_names=[user.firstName],
                        birth_date=user.validatedBirthDate,
                        gender=users_models.GenderEnum.M,
                    )
                ],
            ).model_dump(),
        )
        qf_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)

        bonus_api.apply_for_quotient_familial_bonus(qf_fraud_check)

        assert qf_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert qf_fraud_check.source_data().quotient_familial == config_fraud_check.source_data().quotient_familial
        assert qf_fraud_check.source_data().children == config_fraud_check.source_data().children

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_quotient_familial_too_high(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                http_status_code=200,
                quotient_familial=bonus_schemas.QuotientFamilialContent(
                    provider="CNAF", value=999_999_999, year=2023, month=6, computation_year=2024, computation_month=12
                ),
                children=[
                    bonus_schemas.QuotientFamilialChild(
                        last_name=user.lastName,
                        common_name=None,
                        first_names=[user.firstName],
                        birth_date=user.validatedBirthDate,
                        gender=users_models.GenderEnum.M,
                    )
                ],
            ).model_dump(),
        )
        qf_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)

        bonus_api.apply_for_quotient_familial_bonus(qf_fraud_check)

        assert qf_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert qf_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_custodian_not_found(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                http_status_code=404,
            ),
        )
        qf_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(
            api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=bonus_fixtures.CUSTODIAN_NOT_FOUND_FIXTURE, status_code=404
        )

        bonus_api.apply_for_quotient_familial_bonus(qf_fraud_check)

        assert qf_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert qf_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.CUSTODIAN_NOT_FOUND]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
