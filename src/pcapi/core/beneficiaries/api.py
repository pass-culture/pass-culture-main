from pcapi.core.users import api as users_api
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.models import BeneficiaryImport
from pcapi.models import Deposit
from pcapi.models import ImportStatus
from pcapi.models import UserSQLEntity
from pcapi.models.db import db
from pcapi.models.deposit import DEPOSIT_DEFAULT_AMOUNT

from . import exceptions


def activate_beneficiary(user: UserSQLEntity, deposit_source: str) -> UserSQLEntity:
    if not users_api.is_user_eligible(user):
        raise exceptions.NotEligible()
    user.isBeneficiary = True
    deposit = create_deposit(user, deposit_source=deposit_source)
    db.session.add_all((user, deposit))
    db.session.commit()
    return user


def create_deposit(beneficiary: UserSQLEntity, deposit_source: str) -> Deposit:
    existing_deposits = bool(Deposit.query.filter_by(userId=beneficiary.id).count())
    if existing_deposits:
        raise exceptions.AlreadyActivatedException({"user": ["Cet utilisateur a déjà crédité son pass Culture"]})

    deposit = Deposit(
        amount=DEPOSIT_DEFAULT_AMOUNT,
        source=deposit_source,
        userId=beneficiary.id,
    )
    return deposit


def attach_beneficiary_import_details(
    beneficiary: UserSQLEntity, beneficiary_pre_subscription: BeneficiaryPreSubscription
) -> None:
    beneficiary_import = BeneficiaryImport()

    beneficiary_import.applicationId = beneficiary_pre_subscription.application_id
    beneficiary_import.sourceId = beneficiary_pre_subscription.source_id
    beneficiary_import.source = beneficiary_pre_subscription.source
    beneficiary_import.setStatus(status=ImportStatus.CREATED)

    beneficiary.beneficiaryImports = [beneficiary_import]
