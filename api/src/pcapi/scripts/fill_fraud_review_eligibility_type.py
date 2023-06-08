import argparse
from datetime import timedelta

from sqlalchemy import extract
from sqlalchemy import func

from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models
from pcapi.flask_app import app
from pcapi.models import db


def get_log_message(
    fraud_review: fraud_models.BeneficiaryFraudReview, eligibility: users_models.EligibilityType
) -> str:
    return f"Review from {fraud_review.author.full_name} on {fraud_review.user.full_name} ID: {fraud_review.userId} ({fraud_review.dateReviewed}) -> Expected eligibility: {eligibility}"


def add_eligibility_to_reviews_based_on_deposit(do_update: bool) -> None:
    # Search for deposits that was created less than one minute after fraud review
    query = (
        fraud_models.BeneficiaryFraudReview.query.filter_by(eligibilityType=None)
        .join(
            finance_models.Deposit,
            fraud_models.BeneficiaryFraudReview.userId == finance_models.Deposit.userId,
        )
        .filter(finance_models.Deposit.dateCreated >= fraud_models.BeneficiaryFraudReview.dateReviewed)
        .filter(
            finance_models.Deposit.dateCreated < fraud_models.BeneficiaryFraudReview.dateReviewed + timedelta(minutes=1)
        )
        .with_entities(fraud_models.BeneficiaryFraudReview, finance_models.Deposit.type)
    )

    fraud_reviews_to_update = []

    for fraud_review, deposit_type in query:
        eligibility = (
            users_models.EligibilityType.AGE18
            if deposit_type == finance_models.DepositType.GRANT_18
            else users_models.EligibilityType.UNDERAGE
        )
        fraud_reviews_to_update.append(
            {
                "id": fraud_review.id,
                "eligibilityType": eligibility,
            }
        )
        print(get_log_message(fraud_review, eligibility))

    if do_update:
        db.session.bulk_update_mappings(fraud_models.BeneficiaryFraudReview, fraud_reviews_to_update)
        db.session.commit()


def add_eligibility_to_reviews_based_on_beneficiary_age(do_update: bool) -> None:
    base_query = fraud_models.BeneficiaryFraudReview.query.filter_by(eligibilityType=None).join(
        users_models.User, fraud_models.BeneficiaryFraudReview.userId == users_models.User.id
    )
    reviews_on_adult_beneficiaries_query = base_query.filter(
        extract("years", func.age(fraud_models.BeneficiaryFraudReview.dateReviewed, users_models.User.dateOfBirth))
        >= 18
    )
    reviews_on_underage_beneficiaries_query = base_query.filter(
        extract("years", func.age(fraud_models.BeneficiaryFraudReview.dateReviewed, users_models.User.dateOfBirth)) < 18
    )

    fraud_reviews_to_update = []

    for fraud_review in reviews_on_adult_beneficiaries_query:
        fraud_reviews_to_update.append({"id": fraud_review.id, "eligibilityType": users_models.EligibilityType.AGE18})
        print(get_log_message(fraud_review, users_models.EligibilityType.AGE18))

    for fraud_review in reviews_on_underage_beneficiaries_query:
        fraud_reviews_to_update.append(
            {"id": fraud_review.id, "eligibilityType": users_models.EligibilityType.UNDERAGE}
        )
        print(get_log_message(fraud_review, users_models.EligibilityType.UNDERAGE))

    if do_update:
        db.session.bulk_update_mappings(fraud_models.BeneficiaryFraudReview, fraud_reviews_to_update)
        db.session.commit()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="Fix pro roles in User table")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    add_eligibility_to_reviews_based_on_deposit(do_update=args.not_dry)
    add_eligibility_to_reviews_based_on_beneficiary_age(do_update=args.not_dry)
