from pcapi.models import Deposit
from pcapi.models import User
from pcapi.models import db
from pcapi.models.deposit import DepositType


def does_deposit_exists_for_beneficiary_and_type(beneficiary: User, deposit_type: DepositType):
    return db.session.query(Deposit.query.filter_by(userId=beneficiary.id, type=deposit_type.value).exists()).scalar()
