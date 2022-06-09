from pcapi.core.fraud import models as fraud_models
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models import db


BATCH_SIZE = 1000


def generate_missing_profile_completion_fraud_checks(dry_run: bool = True) -> None:
    print("Fetching users...")
    users_with_profile_completed_but_no_profile_fraud_check = User.query.filter(
        User.city.isnot(None),
        User.activity.isnot(None),
        User.firstName.isnot(None),
        User.lastName.isnot(None),
        ~User.beneficiaryFraudChecks.any(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        ),
    ).with_entities(User.id)
    user_ids = [user_id_tuple[0] for user_id_tuple in users_with_profile_completed_but_no_profile_fraud_check.all()]
    fraud_checks_created_count = 0
    start_index = 0
    print("Creating fraud checks...")
    while start_index < len(user_ids):
        user_ids_batch = user_ids[start_index : start_index + BATCH_SIZE]
        users = User.query.filter(User.id.in_(user_ids_batch)).all()
        for user in users:
            if UserRole.UNDERAGE_BENEFICIARY in user.roles:
                eligibility = EligibilityType.UNDERAGE
            elif UserRole.BENEFICIARY in user.roles:
                eligibility = EligibilityType.AGE18
            else:
                eligibility = user.eligibility
            fraud_check_content = fraud_models.ProfileCompletionContent(
                activity=user.activity,
                city=user.city,
                first_name=user.firstName,
                last_name=user.lastName,
                origin="Created by script. https://passculture.atlassian.net/browse/PC-15549",
                postalCode=user.postalCode,
                school_type=user.schoolType,
            )
            fraud_check = fraud_models.BeneficiaryFraudCheck(
                user=user,
                type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
                resultContent=fraud_check_content,
                status=fraud_models.FraudCheckStatus.OK,
                thirdPartyId=f"profile-completion-{user.id}",
                eligibilityType=eligibility,
                reason=fraud_check_content.origin,
            )
            db.session.add(fraud_check)
            fraud_checks_created_count += 1
        if dry_run:
            db.session.rollback()
            print("Dry run. Would have created %d fraud checks" % fraud_checks_created_count)
        else:
            db.session.commit()
            print("Created %d fraud checks" % fraud_checks_created_count)
        print(f"{start_index} users treated out of {len(user_ids)}")
        start_index += BATCH_SIZE
    print(f"Created {fraud_checks_created_count} profile fraud checks")
    print("Done!")
