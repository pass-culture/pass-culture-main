from datetime import datetime

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.core.fraud import repository as fraud_repository


@pytest.mark.usefixtures("db_session")
class RepositoryTest:
    def should_find_ko_reviews(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudReviewFactory(user=user, review=fraud_models.FraudReviewStatus.KO)

        assert fraud_repository.has_admin_ko_review(user)

    def should_override_ko_with_ok_review(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user, review=fraud_models.FraudReviewStatus.KO, dateReviewed=datetime(2020, 1, 1)
        )
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user, review=fraud_models.FraudReviewStatus.OK, dateReviewed=datetime(2020, 1, 2)
        )

        assert not fraud_repository.has_admin_ko_review(user)

    def should_use_latest_review(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user, review=fraud_models.FraudReviewStatus.OK, dateReviewed=datetime(2020, 1, 1)
        )
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user, review=fraud_models.FraudReviewStatus.KO, dateReviewed=datetime(2020, 1, 2)
        )

        assert fraud_repository.has_admin_ko_review(user)


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
            fraud_models.FraudCheckType.JOUVE,
            fraud_models.FraudCheckType.EDUCONNECT,
            fraud_models.FraudCheckType.UBBLE,
            fraud_models.FraudCheckType.DMS,
        ],
    )
    def should_get_relevant_identity_fraud_check_when_same_eligibility(self, user_eligibility, fraud_check_type):
        age = 17 if user_eligibility == users_models.EligibilityType.UNDERAGE else 18
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=age))
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=user_eligibility, type=fraud_check_type
        )

        assert fraud_repository.get_relevant_identity_fraud_check(user, user_eligibility) == fraud_check

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.AGE17_18,
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
        ],
    )
    @pytest.mark.parametrize("fraud_check_type", [fraud_models.FraudCheckType.UBBLE, fraud_models.FraudCheckType.DMS])
    def should_get_underage_fraud_check_when_applicable_at_eighteen(self, fraud_check_type, eligibility):
        user = users_factories.UserFactory(age=18)
        underage_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_check_type,
            status=fraud_models.FraudCheckStatus.OK,
        )

        fraud_check = fraud_repository.get_relevant_identity_fraud_check(user, eligibility)

        assert fraud_check == underage_fraud_check

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.AGE17_18,
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
        ],
    )
    @pytest.mark.parametrize("fraud_check_type", [fraud_models.FraudCheckType.UBBLE, fraud_models.FraudCheckType.DMS])
    def should_get_age_17_18_fraud_check_when_applicable_at_eighteen(self, eligibility, fraud_check_type):
        user = users_factories.UserFactory(age=18)
        age_17_18_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=fraud_check_type,
            status=fraud_models.FraudCheckStatus.OK,
        )

        relevant_fraud_check = fraud_repository.get_relevant_identity_fraud_check(user, eligibility)

        assert relevant_fraud_check == age_17_18_fraud_check

    @pytest.mark.parametrize(
        "underage_eligibility", [users_models.EligibilityType.AGE17_18, users_models.EligibilityType.UNDERAGE]
    )
    def should_not_get_underage_fraud_check_when_not_applicable_at_eighteen(self, underage_eligibility):
        user = users_factories.UserFactory(age=17)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=underage_eligibility,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        year_when_user_is_eighteen = datetime.utcnow() + relativedelta(years=1)
        with time_machine.travel(year_when_user_is_eighteen):
            relevant_fraud_check = fraud_repository.get_relevant_identity_fraud_check(
                user, users_models.EligibilityType.AGE18
            )

        assert relevant_fraud_check is None

    @pytest.mark.parametrize(
        "fraud_check_type",
        [fraud_models.FraudCheckType.EDUCONNECT, fraud_models.FraudCheckType.UBBLE, fraud_models.FraudCheckType.DMS],
    )
    def should_get_age_17_18_fraud_check_when_applicable_for_underage(self, fraud_check_type):
        user = users_factories.UserFactory(age=17)
        age_17_18_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=fraud_check_type,
            status=fraud_models.FraudCheckStatus.OK,
        )

        underage_relevant_fraud_check = fraud_repository.get_relevant_identity_fraud_check(
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
            fraud_models.FraudCheckType.UBBLE,
            fraud_models.FraudCheckType.DMS,
            fraud_models.FraudCheckType.EDUCONNECT,
            fraud_models.FraudCheckType.JOUVE,
        ],
    )
    def should_get_no_fraud_check_when_eligibility_mismatch(
        self, user_eligibility, fraud_check_eligibility, fraud_check_type
    ):
        age = 17 if user_eligibility == users_models.EligibilityType.UNDERAGE else 18
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=age))
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=fraud_check_eligibility, type=fraud_check_type
        )

        assert fraud_repository.get_relevant_identity_fraud_check(user, user_eligibility) is None

    def should_get_ok_fraud_check_if_any(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=17))
        fraud_check_ok = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=fraud_models.FraudCheckStatus.KO,
        )

        assert (
            fraud_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.UNDERAGE)
            == fraud_check_ok
        )

    def should_get_pending_fraud_check_when_no_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=17))
        fraud_check_pending = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=fraud_models.FraudCheckStatus.PENDING,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=fraud_models.FraudCheckStatus.KO,
        )

        assert (
            fraud_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.UNDERAGE)
            == fraud_check_pending
        )

    def should_get_latest_ko_fraud_check_when_no_pending_or_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=17))
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=fraud_models.FraudCheckStatus.KO,
        )
        fraud_check_ko = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            status=fraud_models.FraudCheckStatus.KO,
        )

        assert (
            fraud_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.UNDERAGE)
            == fraud_check_ko
        )
