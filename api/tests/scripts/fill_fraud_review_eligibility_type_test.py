from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.finance.enum import DepositType
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.factories import BeneficiaryFraudReviewFactory
from pcapi.core.users import models as users_models
from pcapi.core.users.factories import DepositGrantFactory
from pcapi.core.users.factories import UserFactory
from pcapi.scripts.fill_fraud_review_eligibility_type import add_eligibility_to_reviews_based_on_beneficiary_age
from pcapi.scripts.fill_fraud_review_eligibility_type import add_eligibility_to_reviews_based_on_deposit


@pytest.mark.usefixtures("db_session")
class FillFraudReviewEligibilityTypeTest:
    @pytest.mark.parametrize(
        "deposit_type",
        [DepositType.GRANT_18, DepositType.GRANT_15_17],
    )
    def test_add_eligibility_to_reviews_based_on_deposit(self, deposit_type: DepositType) -> None:
        beneficiary = UserFactory()
        BeneficiaryFraudReviewFactory(user=beneficiary, eligibilityType=None)
        DepositGrantFactory(user=beneficiary, type=deposit_type)

        add_eligibility_to_reviews_based_on_deposit(do_update=True)

        fraud_review: fraud_models.BeneficiaryFraudReview = fraud_models.BeneficiaryFraudReview.query.first()

        assert (
            fraud_review.eligibilityType == users_models.EligibilityType.AGE18
            if deposit_type == DepositType.GRANT_18
            else users_models.EligibilityType.UNDERAGE
        )

    @pytest.mark.parametrize(
        "deposit_creation_date",
        [datetime.utcnow() + timedelta(minutes=30), datetime.utcnow() - timedelta(minutes=1)],
    )
    def test_not_add_eligibility_to_reviews_based_on_deposit(self, deposit_creation_date: datetime) -> None:
        beneficiary = UserFactory()
        BeneficiaryFraudReviewFactory(user=beneficiary, eligibilityType=None)
        DepositGrantFactory(user=beneficiary, dateCreated=deposit_creation_date)

        add_eligibility_to_reviews_based_on_deposit(do_update=True)

        fraud_review: fraud_models.BeneficiaryFraudReview = fraud_models.BeneficiaryFraudReview.query.first()

        assert fraud_review.eligibilityType is None

    @pytest.mark.parametrize(
        "beneficiary_age",
        [19, 18, 17, 16, 15],
    )
    def test_add_eligibility_to_reviews_based_on_beneficiary(self, beneficiary_age: int) -> None:
        beneficiary = UserFactory(dateOfBirth=(datetime.utcnow() - relativedelta(years=beneficiary_age)).date())
        BeneficiaryFraudReviewFactory(user=beneficiary, eligibilityType=None)

        add_eligibility_to_reviews_based_on_beneficiary_age(do_update=True)

        fraud_review: fraud_models.BeneficiaryFraudReview = fraud_models.BeneficiaryFraudReview.query.first()
        expected_eligibility = (
            users_models.EligibilityType.AGE18 if beneficiary_age >= 18 else users_models.EligibilityType.UNDERAGE
        )

        assert fraud_review.eligibilityType == expected_eligibility
