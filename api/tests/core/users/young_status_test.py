import datetime

import attrs
from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import young_status


pytestmark = pytest.mark.usefixtures("db_session")


def _with_age(age):
    return datetime.datetime.utcnow() - relativedelta(years=age)


class UserStatusTest:
    class EligibleTest:
        @pytest.mark.parametrize("age", [15, 16, 17])
        def should_be_eligible_when_age_is_between_15_and_17(self, age):
            user = users_factories.UserFactory(dateOfBirth=_with_age(age))
            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
            )

        def should_be_eligible_when_at_18yo(self):
            user = users_factories.UserFactory(dateOfBirth=_with_age(18))
            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
            )

        def should_be_eligible_when_at_19yo_with_pending_dms_application_started_at_18yo(self):
            user = users_factories.UserFactory(dateOfBirth=_with_age(19))
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.DMS,
                resultContent=fraud_factories.DMSContentFactory(
                    registration_datetime=datetime.datetime.utcnow() - relativedelta(years=1)
                ),
            )
            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
            )

        @pytest.mark.parametrize(
            "fraud_status", [fraud_models.FraudCheckStatus.STARTED, fraud_models.FraudCheckStatus.PENDING]
        )
        def should_be_eligible_when_subscription_is_pending(self, fraud_status):
            user = users_factories.UserFactory(dateOfBirth=_with_age(18))
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.AGE18,
                type=fraud_models.FraudCheckType.DMS,
                status=fraud_status,
            )

            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
            )

        @pytest.mark.parametrize(
            "fraud_status", [fraud_models.FraudCheckStatus.STARTED, fraud_models.FraudCheckStatus.PENDING]
        )
        @pytest.mark.parametrize("age", [15, 16, 17])
        def should_be_eligible_when_subscription_is_pending_for_an_underage_user(self, fraud_status, age):
            user = users_factories.UserFactory(dateOfBirth=_with_age(age))
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                type=fraud_models.FraudCheckType.DMS,
                status=fraud_status,
            )

            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
            )

        def test_be_eligible_when_has_subscription_issues(self):
            user = users_factories.UserFactory(
                dateOfBirth=_with_age(18),
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
                user=user,
                status=fraud_models.FraudCheckStatus.OK,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                type=fraud_models.FraudCheckType.UBBLE,
                user=user,
                status=fraud_models.FraudCheckStatus.SUSPICIOUS,
                reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED],
            )

            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
            )

    def should_be_non_eligible_when_too_young(self):
        user = users_factories.UserFactory(dateOfBirth=_with_age(15) + relativedelta(days=1))
        assert young_status.young_status(user) == young_status.NonEligible()

    def should_be_non_eligible_when_too_old(self):
        user = users_factories.UserFactory(dateOfBirth=_with_age(19) - relativedelta(days=1))
        assert young_status.young_status(user) == young_status.NonEligible()

    def should_be_beneficiary_when_18yo_and_have_deposit(self):
        user = users_factories.BeneficiaryGrant18Factory()
        assert young_status.young_status(user) == young_status.Beneficiary()

    def should_be_beneficiary_when_underage_and_have_deposit(self):
        user = users_factories.UnderageBeneficiaryFactory()
        assert young_status.young_status(user) == young_status.Beneficiary()

    def should_be_ex_beneficiary_when_beneficiary_have_his_deposit_expired(self):
        user = users_factories.BeneficiaryGrant18Factory(
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(days=1)
        )
        assert young_status.young_status(user) == young_status.ExBeneficiary()

    def should_be_suspended_when_account_is_not_active(self):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        assert young_status.young_status(user) == young_status.Suspended()

    def test_is_not_mutable(self):
        status = young_status.Suspended()
        with pytest.raises(attrs.exceptions.FrozenInstanceError):
            status.status_type = young_status.YoungStatusType.BENEFICIARY
