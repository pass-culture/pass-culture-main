import logging
from typing import Iterable

import pcapi.core.fraud.models as fraud_models
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.users import constants
from pcapi.core.users.api import suspend_account
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.deposit import Deposit


logger = logging.getLogger(__name__)


def _find_users_to_suspend(user_ids: set) -> set:
    return set(
        user_id[0] for user_id in Deposit.query.filter(Deposit.userId.in_(user_ids)).with_entities(Deposit.userId)
    )


def _delete_users_and_favorites(user_ids: set) -> None:
    for user_id in user_ids:
        logger.info("Deleting user and their data", extra={"user": user_id})
        Favorite.query.filter(Favorite.userId == user_id).delete()
        BeneficiaryImportStatus.query.filter(
            BeneficiaryImportStatus.beneficiaryImportId == BeneficiaryImport.id,
            BeneficiaryImport.beneficiaryId == user_id,
        ).delete(synchronize_session=False)
        BeneficiaryImport.query.filter(BeneficiaryImport.beneficiaryId == user_id).delete(synchronize_session=False)
        fraud_models.BeneficiaryFraudResult.query.filter_by(userId=user_id).delete(synchronize_session=False)
        fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user_id).delete(synchronize_session=False)
        fraud_models.BeneficiaryFraudReview.query.filter_by(userId=user_id).delete(synchronize_session=False)
        user_offerers: list[UserOfferer] = UserOfferer.query.filter(UserOfferer.userId == user_id).all()
        for user_offerer in user_offerers:
            if user_offerer.isValidated and user_offerer.offerer.isValidated:
                raise Exception("Trying to delete a pro user with a valid offerer")
            db.session.delete(user_offerer)
        User.query.filter(User.id == user_id).delete()
        db.session.commit()


def _suspend_users(user_ids: set, admin_email_used: str) -> None:
    admin = User.query.filter_by(email=admin_email_used, isAdmin=True).one()
    for user_id in user_ids:
        user = User.query.get(user_id)
        suspend_account(user, constants.SuspensionReason.UPON_USER_REQUEST, admin)


def suspend_or_delete_users_by_email(admin_email: str, user_emails: Iterable[str]) -> None:
    logger.info("Batch user suspension and deletion", extra={"admin": admin_email})
    user_ids = {user_id for user_id, in User.query.filter(User.email.in_(user_emails)).with_entities(User.id)}
    users_to_suspend = _find_users_to_suspend(user_ids)
    users_to_delete = user_ids - users_to_suspend
    print(f"Deleting {len(users_to_delete)} users...")
    _delete_users_and_favorites(users_to_delete)
    print(f"Suspending {len(users_to_suspend)} users...")
    _suspend_users(users_to_suspend, admin_email)
    print("[DELETE OR SUSPEND USER FROM FILE] END")


def suspend_or_delete_from_file(path: str, admin_email: str) -> None:
    user_emails = set()
    with open(path) as fp:
        user_emails = {line.strip() for line in fp.readlines()}
    suspend_or_delete_users_by_email(admin_email, user_emails)
