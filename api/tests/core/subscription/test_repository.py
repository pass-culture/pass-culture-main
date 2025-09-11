from datetime import datetime

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
import pcapi.core.subscription.repository as subscription_repository
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models


@pytest.mark.usefixtures("db_session")
class RepositoryTest:
    def should_find_ko_reviews(self):
        user = users_factories.UserFactory()
        subscription_factories.BeneficiaryFraudReviewFactory(user=user, review=subscription_models.FraudReviewStatus.KO)

        assert subscription_repository.has_admin_ko_review(user)

    def should_override_ko_with_ok_review(self):
        user = users_factories.UserFactory()
        subscription_factories.BeneficiaryFraudReviewFactory(
            user=user, review=subscription_models.FraudReviewStatus.KO, dateReviewed=datetime(2020, 1, 1)
        )
        subscription_factories.BeneficiaryFraudReviewFactory(
            user=user, review=subscription_models.FraudReviewStatus.OK, dateReviewed=datetime(2020, 1, 2)
        )

        assert not subscription_repository.has_admin_ko_review(user)

    def should_use_latest_review(self):
        user = users_factories.UserFactory()
        subscription_factories.BeneficiaryFraudReviewFactory(
            user=user, review=subscription_models.FraudReviewStatus.OK, dateReviewed=datetime(2020, 1, 1)
        )
        subscription_factories.BeneficiaryFraudReviewFactory(
            user=user, review=subscription_models.FraudReviewStatus.KO, dateReviewed=datetime(2020, 1, 2)
        )

        assert subscription_repository.has_admin_ko_review(user)


@pytest.mark.usefixtures("db_session")
class GetRelevantFraudCheckTest:
    @pytest.mark.parametrize(
        "user_eligibility",
        [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
            users_models.EligibilityType.AGE17_18,
        ],
    )
    @pytest.mark.parametrize(
        "fraud_check_type",
        [
            subscription_models.FraudCheckType.JOUVE,
            subscription_models.FraudCheckType.EDUCONNECT,
            subscription_models.FraudCheckType.UBBLE,
            subscription_models.FraudCheckType.DMS,
        ],
    )
    def should_get_relevant_identity_fraud_check_when_same_eligibility(self, user_eligibility, fraud_check_type):
        age = 17 if user_eligibility == users_models.EligibilityType.UNDERAGE else 18
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=age))
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=user_eligibility, type=fraud_check_type
        )

        assert subscription_repository.get_relevant_identity_fraud_check(user, user_eligibility) == fraud_check

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.AGE17_18,
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
        ],
    )
    @pytest.mark.parametrize(
        "fraud_check_type", [subscription_models.FraudCheckType.UBBLE, subscription_models.FraudCheckType.DMS]
    )
    def should_get_underage_fraud_check_when_applicable_at_eighteen(self, fraud_check_type, eligibility):
        user = users_factories.UserFactory(age=18)
        underage_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_check_type,
            status=subscription_models.FraudCheckStatus.OK,
        )

        fraud_check = subscription_repository.get_relevant_identity_fraud_check(user, eligibility)

        assert fraud_check == underage_fraud_check

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.AGE17_18,
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
        ],
    )
    @pytest.mark.parametrize(
        "fraud_check_type", [subscription_models.FraudCheckType.UBBLE, subscription_models.FraudCheckType.DMS]
    )
    def should_get_age_17_18_fraud_check_when_applicable_at_eighteen(self, eligibility, fraud_check_type):
        user = users_factories.UserFactory(age=18)
        age_17_18_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=fraud_check_type,
            status=subscription_models.FraudCheckStatus.OK,
        )

        relevant_fraud_check = subscription_repository.get_relevant_identity_fraud_check(user, eligibility)

        assert relevant_fraud_check == age_17_18_fraud_check

    @pytest.mark.parametrize(
        "underage_eligibility", [users_models.EligibilityType.AGE17_18, users_models.EligibilityType.UNDERAGE]
    )
    def should_not_get_underage_fraud_check_when_not_applicable_at_eighteen(self, underage_eligibility):
        user = users_factories.UserFactory(age=17)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=underage_eligibility,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
        )

        year_when_user_is_eighteen = datetime.utcnow() + relativedelta(years=1)
        with time_machine.travel(year_when_user_is_eighteen):
            relevant_fraud_check = subscription_repository.get_relevant_identity_fraud_check(
                user, users_models.EligibilityType.AGE18
            )

        assert relevant_fraud_check is None

    @pytest.mark.parametrize(
        "fraud_check_type",
        [
            subscription_models.FraudCheckType.EDUCONNECT,
            subscription_models.FraudCheckType.UBBLE,
            subscription_models.FraudCheckType.DMS,
        ],
    )
    def should_get_age_17_18_fraud_check_when_applicable_for_underage(self, fraud_check_type):
        user = users_factories.UserFactory(age=17)
        age_17_18_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=fraud_check_type,
            status=subscription_models.FraudCheckStatus.OK,
        )

        underage_relevant_fraud_check = subscription_repository.get_relevant_identity_fraud_check(
            user, users_models.EligibilityType.UNDERAGE
        )

        assert underage_relevant_fraud_check == age_17_18_fraud_check

    @pytest.mark.parametrize(
        "user_eligibility, fraud_check_eligibility",
        [
            (users_models.EligibilityType.UNDERAGE, users_models.EligibilityType.AGE18),
            (users_models.EligibilityType.AGE18, users_models.EligibilityType.UNDERAGE),
        ],
    )
    @pytest.mark.parametrize(
        "fraud_check_type",
        [
            subscription_models.FraudCheckType.UBBLE,
            subscription_models.FraudCheckType.DMS,
            subscription_models.FraudCheckType.EDUCONNECT,
            subscription_models.FraudCheckType.JOUVE,
        ],
    )
    def should_get_no_fraud_check_when_eligibility_mismatch(
        self, user_eligibility, fraud_check_eligibility, fraud_check_type
    ):
        age = 17 if user_eligibility == users_models.EligibilityType.UNDERAGE else 18
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=age))
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=fraud_check_eligibility, type=fraud_check_type
        )

        assert subscription_repository.get_relevant_identity_fraud_check(user, user_eligibility) is None

    def should_get_ok_fraud_check_if_any(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=17))
        fraud_check_ok = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=subscription_models.FraudCheckStatus.KO,
        )

        assert (
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.UNDERAGE)
            == fraud_check_ok
        )

    def should_get_pending_fraud_check_when_no_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=17))
        fraud_check_pending = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=subscription_models.FraudCheckStatus.PENDING,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=subscription_models.FraudCheckStatus.KO,
        )

        assert (
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.UNDERAGE)
            == fraud_check_pending
        )

    def should_get_latest_ko_fraud_check_when_no_pending_or_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=17))
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=subscription_models.FraudCheckStatus.KO,
        )
        fraud_check_ko = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=subscription_models.FraudCheckStatus.KO,
        )

        assert (
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.UNDERAGE)
            == fraud_check_ko
        )
