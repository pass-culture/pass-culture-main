import datetime

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.connectors import api_particulier
from pcapi.core.finance import models as finance_models
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import api as bonus_api
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.subscription.bonus import staging_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models

from tests.core.subscription.bonus import bonus_fixtures


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(ENABLE_PARTICULIER_API_MOCK=True)
class StagingQuotientFamilialTest:
    def test_mock_eligible_quotient_familial(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                http_status_code=200,
                quotient_familial=bonus_schemas.QuotientFamilialContent(
                    provider="CNAF", value=123, year=2023, month=6, computation_year=2024, computation_month=12
                ),
                children=[
                    bonus_schemas.BonusCreditPerson(
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

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_householder_eligible_quotient_familial(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                http_status_code=200,
                quotient_familial=bonus_schemas.QuotientFamilialContent(
                    provider="CNAF", value=123, year=2023, month=6, computation_year=2024, computation_month=12
                ),
                householders=[
                    bonus_schemas.BonusCreditPerson(
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

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_not_in_tax_household(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                http_status_code=200,
                quotient_familial=bonus_schemas.QuotientFamilialContent(
                    provider="CNAF", value=123, year=2023, month=6, computation_year=2024, computation_month=12
                ),
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
        assert qf_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
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
                    bonus_schemas.BonusCreditPerson(
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

    def test_mock_application_not_found(self, requests_mock):
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
            api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
            json=bonus_fixtures.APPLICATION_NOT_FOUND_FIXTURE,
            status_code=404,
        )

        bonus_api.apply_for_quotient_familial_bonus(qf_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["nomNaissance"] == [staging_api.QF_APPLICATION_NOT_FOUND.last_name.upper()]

        assert qf_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert qf_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.APPLICATION_NOT_FOUND]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_person_not_found(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                http_status_code=422,
            ),
        )
        qf_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(
            api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
            json=bonus_fixtures.PERSON_NOT_FOUND_FIXTURE,
            status_code=422,
        )

        bonus_api.apply_for_quotient_familial_bonus(qf_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["codeCogInseePaysNaissance"] == [staging_api.PERSON_NOT_FOUND.birth_country_cog_code]

        assert qf_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert qf_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.PERSON_NOT_FOUND]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_data_provider_error(self, requests_mock):
        twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                http_status_code=502,
            ),
        )
        qf_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
            updatedAt=twelve_hours_ago,
        )
        requests_mock.get(
            api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
            json=bonus_fixtures.DATA_PROVIDER_ERROR,
            status_code=502,
        )

        with pytest.raises(api_particulier.ParticulierApiException):
            bonus_api.apply_for_quotient_familial_bonus(qf_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["nomNaissance"] == [staging_api.DATA_PROVIDER_ERROR.last_name.upper()]

        assert qf_fraud_check.updatedAt > twelve_hours_ago

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(ENABLE_PARTICULIER_API_MOCK=True)
class StagingDisabledAdultAllowanceTest:
    def test_mock_disabled_adult_allowance_recipient(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=200,
                is_disability_recipient=True,
            ).model_dump(),
        )
        aah_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=bonus_fixtures.AAH_RECIPIENT_RESPONSE)

        bonus_api.apply_for_adult_disability_bonus(aah_fraud_check)

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_adult_allowance_non_recipient(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=200,
                is_disability_recipient=False,
            ).model_dump(),
        )
        aah_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(api_particulier.AAH_ENDPOINT, json=bonus_fixtures.AAH_NOT_RECIPIENT_RESPONSE)

        bonus_api.apply_for_adult_disability_bonus(aah_fraud_check)

        assert aah_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert aah_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_RECIPIENT]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_adult_allowance_application_not_found(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=404,
            ).model_dump(),
        )
        aah_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(
            api_particulier.AAH_ENDPOINT,
            json=bonus_fixtures.APPLICATION_NOT_FOUND_FIXTURE,
            status_code=404,
        )

        bonus_api.apply_for_adult_disability_bonus(aah_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["nomNaissance"] == [staging_api.DISABILITY_APPLICATION_NOT_FOUND.last_name.upper()]

        assert aah_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert aah_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.APPLICATION_NOT_FOUND]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_adult_allowance_person_not_found(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=422,
            ).model_dump(),
        )
        aah_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(
            api_particulier.AAH_ENDPOINT,
            json=bonus_fixtures.PERSON_NOT_FOUND_FIXTURE,
            status_code=422,
        )

        bonus_api.apply_for_adult_disability_bonus(aah_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["nomNaissance"] == [staging_api.PERSON_NOT_FOUND.last_name.upper()]

        assert aah_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert aah_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.PERSON_NOT_FOUND]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_adult_allowance_data_provider_error(self, requests_mock):
        twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=502,
            ).model_dump(),
        )
        aah_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
            updatedAt=twelve_hours_ago,
        )
        requests_mock.get(
            api_particulier.AAH_ENDPOINT,
            json=bonus_fixtures.DATA_PROVIDER_ERROR,
            status_code=502,
        )

        with pytest.raises(api_particulier.ParticulierApiException):
            bonus_api.apply_for_adult_disability_bonus(aah_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["nomNaissance"] == [staging_api.DATA_PROVIDER_ERROR.last_name.upper()]

        assert aah_fraud_check.updatedAt > twelve_hours_ago

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(ENABLE_PARTICULIER_API_MOCK=True)
class StagingDisabledChildEducationAllowanceTest:
    def test_mock_disabled_child_education_allowance_recipient(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=200,
                disability_recipient_status=bonus_schemas.DisabledChildEducationRecipientStatus.RECIPIENT,
            ).model_dump(),
        )
        aeeh_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=bonus_fixtures.AEEH_RECIPIENT_RESPONSE)

        bonus_api.apply_for_disabled_child_education_bonus(aeeh_fraud_check)

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_child_education_allowance_right_opening(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=200,
                disability_recipient_status=bonus_schemas.DisabledChildEducationRecipientStatus.RIGHT_OPENING,
            ).model_dump(),
        )
        aeeh_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=bonus_fixtures.AEEH_OPENING_RIGHTS_RESPONSE)

        bonus_api.apply_for_disabled_child_education_bonus(aeeh_fraud_check)

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_child_education_allowance_non_recipient(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=200,
                disability_recipient_status=bonus_schemas.DisabledChildEducationRecipientStatus.NON_RECIPIENT,
            ).model_dump(),
        )
        aeeh_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(api_particulier.AEEH_ENDPOINT, json=bonus_fixtures.AEEH_NOT_RECIPIENT_RESPONSE)

        bonus_api.apply_for_disabled_child_education_bonus(aeeh_fraud_check)

        assert aeeh_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert aeeh_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_RECIPIENT]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_child_education_allowance_application_not_found(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=404,
            ).model_dump(),
        )
        aeeh_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(
            api_particulier.AEEH_ENDPOINT,
            json=bonus_fixtures.APPLICATION_NOT_FOUND_FIXTURE,
            status_code=404,
        )

        bonus_api.apply_for_disabled_child_education_bonus(aeeh_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["nomNaissance"] == [staging_api.DISABILITY_APPLICATION_NOT_FOUND.last_name.upper()]

        assert aeeh_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert aeeh_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.APPLICATION_NOT_FOUND]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_child_education_allowance_person_not_found(self, requests_mock):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=422,
            ).model_dump(),
        )
        aeeh_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        requests_mock.get(
            api_particulier.AEEH_ENDPOINT,
            json=bonus_fixtures.PERSON_NOT_FOUND_FIXTURE,
            status_code=422,
        )

        bonus_api.apply_for_disabled_child_education_bonus(aeeh_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["nomNaissance"] == [staging_api.PERSON_NOT_FOUND.last_name.upper()]

        assert aeeh_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert aeeh_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.PERSON_NOT_FOUND]

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

    def test_mock_disabled_adult_allowance_data_provider_error(self, requests_mock):
        twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.MOCK_CONFIG,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                http_status_code=502,
            ).model_dump(),
        )
        aeeh_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
            updatedAt=twelve_hours_ago,
        )
        requests_mock.get(
            api_particulier.AEEH_ENDPOINT,
            json=bonus_fixtures.DATA_PROVIDER_ERROR,
            status_code=502,
        )

        with pytest.raises(api_particulier.ParticulierApiException):
            bonus_api.apply_for_disabled_child_education_bonus(aeeh_fraud_check)

        query_string = requests_mock.request_history[0].qs
        assert query_string["nomNaissance"] == [staging_api.DISABLED_CHILD_DATA_PROVIDER_ERROR.last_name.upper()]

        assert aeeh_fraud_check.updatedAt > twelve_hours_ago

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
