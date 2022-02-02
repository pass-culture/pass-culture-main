from datetime import date

from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.ubble.api import handle_validation_errors
from pcapi.core.users import models as users_models
from pcapi.models import db


def allow_ubble_retry_for_users_signed_before_v170(dry_run: bool = True) -> None:
    users = (
        users_models.User.query.join(fraud_models.BeneficiaryFraudCheck)
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.KO,
            fraud_models.BeneficiaryFraudCheck.dateCreated < date(2022, 1, 18),
            users_models.User.is_beneficiary == False,
        )
        .all()
    )
    print("len(users)", len(users))
    users_to_activate = []
    ## trouver les users qui ont déposé un dossier DMS, les exclure
    k = 0
    for user in users:
        if k % 500 == 0:
            print(k)
        k += 1
        has_dms = db.session.query(
            fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user, type=fraud_models.FraudCheckType.DMS).exists()
        ).scalar()
        if not has_dms and fraud_api.ubble_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility):
            users_to_activate.append(user)
    print("users_to_activate length", len(users_to_activate))
    return users_to_activate
    if dry_run:
        return


def send_message(users_to_activate):
    error_ids = []
    no_fraud_check = []
    success_ids = []
    for user in users_to_activate:
        fraud_check = (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.KO
            )
            .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
            .first()
        )
        if not fraud_check:
            no_fraud_check.append(user.id)
            continue
        try:
            handle_validation_errors(user, fraud_check.reasonCodes)
            success_ids.append(user.id)
        except Exception as exc:
            print("error: ", user.id, exc)
            error_ids.append(user.id)
    return error_ids, success_ids, no_fraud_check
