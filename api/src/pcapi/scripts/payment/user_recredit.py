from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import joinedload

from pcapi.core.payments import models as payments_models
import pcapi.core.payments.conf as deposit_conf
from pcapi.core.users import models as users_models
from pcapi.repository import repository
from pcapi.repository import transaction


logger = logging.getLogger(__name__)


def has_celebrated_their_birthday_since_activation(user: users_models.User) -> bool:
    return user.deposit_activation_date is not None and user.deposit_activation_date.date() <= user.latest_birthday


def has_been_recredited(user: users_models.User) -> bool:
    if len(user.deposit.recredits) == 0:
        return False

    if user.deposit.recredits[0].recreditType != deposit_conf.RECREDIT_TYPE_AGE_MAPPING[user.age]:
        return False

    return True


def recredit_underage_users() -> None:
    sixteen_years_ago = datetime.now() - relativedelta(years=16)
    eighteen_years_ago = datetime.now() - relativedelta(years=18)

    users: list[users_models.User] = (
        users_models.User.query.filter(users_models.User.has_underage_beneficiary_role)
        .filter(users_models.User.dateOfBirth > eighteen_years_ago)
        .filter(users_models.User.dateOfBirth <= sixteen_years_ago)
        .options(joinedload(users_models.User.deposits).joinedload(payments_models.Deposit.recredits))
        .all()
    )
    users_to_recredit = [
        user for user in users if has_celebrated_their_birthday_since_activation(user) and not has_been_recredited(user)
    ]
    recredits = [
        payments_models.Recredit(
            depositId=user.deposit.id,
            deposit=user.deposit,
            amount=deposit_conf.RECREDIT_TYPE_AMOUNT_MAPPING[deposit_conf.RECREDIT_TYPE_AGE_MAPPING[user.age]],
            recreditType=deposit_conf.RECREDIT_TYPE_AGE_MAPPING[user.age],
        )
        for user in users_to_recredit
    ]
    with transaction():
        for recredit in recredits:
            recredit.deposit.amount += recredit.amount

        repository.save(*recredits)
    logger.info("Recredited %s underage users deposits", len(users_to_recredit))
