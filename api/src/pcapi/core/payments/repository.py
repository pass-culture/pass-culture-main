from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
from pcapi.core.users.models import User
from pcapi.models import db


def does_deposit_exists_for_beneficiary_and_type(beneficiary: User, deposit_type: DepositType):  # type: ignore [no-untyped-def]
    return db.session.query(Deposit.query.filter_by(userId=beneficiary.id, type=deposit_type.value).exists()).scalar()
