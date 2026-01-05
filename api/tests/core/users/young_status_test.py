import dataclasses

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import young_status
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


def _with_age(age):
    return date_utils.get_naive_utc_now() - relativedelta(years=age)


class YoungStatusTest:
    class EligibleTest:
        @pytest.mark.parametrize("age", [17, 18])
        def should_be_eligible_when_age_is_between_17_and_18(self, age):
            user = users_factories.UserFactory(dateOfBirth=_with_age(age))
            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
            )

        def should_be_eligible_when_at_19yo_with_pending_dms_application_started_at_18yo(self):
            user = users_factories.UserFactory(dateOfBirth=_with_age(19))
            subscription_factories.BeneficiaryFraudCheckFactory(
                resultContent=subscription_factories.DMSContentFactory(
                    registration_datetime=date_utils.get_naive_utc_now() - relativedelta(years=1)
                ),
                type=subscription_models.FraudCheckType.DMS,
                user=user,
            )
            assert young_status.young_status(user).status_type == young_status.YoungStatusType.ELIGIBLE

        def should_be_eligible_when_subscription_is_pending(self):
            user = users_factories.UserFactory(
                dateOfBirth=_with_age(18), phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.OK,
                type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
                user=user,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.PENDING,
                type=subscription_models.FraudCheckType.DMS,
                user=user,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.OK,
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                user=user,
            )

            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
            )

        def should_have_subscription_pending_when_dms_is_started_for_underage(self):
            user = users_factories.UserFactory(
                dateOfBirth=_with_age(17), phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.OK,
                type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.STARTED,
                type=subscription_models.FraudCheckType.DMS,
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.OK,
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
            )

        def should_have_subscription_pending_when_dms_is_started(self):
            user = users_factories.UserFactory(
                dateOfBirth=_with_age(18), phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.OK,
                type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
                user=user,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.STARTED,
                type=subscription_models.FraudCheckType.DMS,
                user=user,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.OK,
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                user=user,
            )

            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
            )

        def should_be_eligible_when_subscription_is_pending_for_an_underage_user(self):
            user = users_factories.UserFactory(dateOfBirth=_with_age(17))
            subscription_factories.BeneficiaryFraudCheckFactory(
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
                status=subscription_models.FraudCheckStatus.OK,
                user=user,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                status=subscription_models.FraudCheckStatus.PENDING,
                type=subscription_models.FraudCheckType.DMS,
                user=user,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                status=subscription_models.FraudCheckStatus.OK,
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                user=user,
            )

            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
            )

        def should_be_eligible_when_has_subscription_issues(self):
            user = users_factories.UserFactory(
                dateOfBirth=_with_age(18),
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
                status=subscription_models.FraudCheckStatus.OK,
                user=user,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.KO,
                reasonCodes=[subscription_models.FraudReasonCode.INVALID_ID_PIECE_NUMBER],
                type=subscription_models.FraudCheckType.UBBLE,
                user=user,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                status=subscription_models.FraudCheckStatus.OK,
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                user=user,
            )

            assert young_status.young_status(user) == young_status.Eligible(
                subscription_status=young_status.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
            )

    def should_be_non_eligible_when_too_young(self):
        # 15 years and 1 day. We add 2 days to be sure that the test will not fail on the 28th of February.
        user = users_factories.UserFactory(dateOfBirth=_with_age(15) + relativedelta(days=2))
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
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(days=1)
        )
        assert young_status.young_status(user) == young_status.ExBeneficiary()

    def should_be_suspended_when_account_is_not_active(self):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        assert young_status.young_status(user) == young_status.Suspended()

    def test_is_not_mutable(self):
        status = young_status.Suspended()
        with pytest.raises(dataclasses.FrozenInstanceError):
            status.status_type = young_status.YoungStatusType.BENEFICIARY

    @pytest.mark.parametrize(
        "review_status",
        [
            subscription_models.FraudReviewStatus.OK,
            subscription_models.FraudReviewStatus.KO,
            subscription_models.FraudReviewStatus.REDIRECTED_TO_DMS,
        ],
    )
    def should_be_beneficiary_when_beneficiary_with_any_admin_review(self, review_status):
        user = users_factories.BeneficiaryGrant18Factory()
        subscription_factories.BeneficiaryFraudReviewFactory(user=user, review=review_status)

        assert young_status.young_status(user) == young_status.Beneficiary()
