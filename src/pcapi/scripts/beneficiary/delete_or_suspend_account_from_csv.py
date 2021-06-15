import csv
import logging

from pcapi.core.users import constants
from pcapi.core.users.api import suspend_account
from pcapi.models import Deposit
from pcapi.models import Favorite
from pcapi.models import User
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def run(csv_file_path: str) -> None:
    logger.info("[DELETE OR SUSPEND USER FROM FILE] START")
    logger.info("[DELETE OR SUSPEND USER FROM FILE] STEP 1 - Lecture du fichier CSV")
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        logger.info("[DELETE OR SUSPEND USER FROM FILE] STEP 2 - Suppression des utilisateurs")
        for row in csv_reader:
            _delete_or_suspend_account_from_csv(row[0])
    logger.info("[DELETE OR SUSPEND USER FROM FILE] END")


def _delete_or_suspend_account_from_csv(user_email: str) -> None:
    # 1 find user
    user = User.query.filter(User.email == user_email).first()
    if not user:
        logger.info("[DELETE OR SUSPEND USER FROM FILE] user %s not found", user_email)
        return
    # 2 has deposit -> suspend account
    has_deposit = Deposit.query.filter(Deposit.userId == user.id).first()
    if has_deposit:
        admin = User.query.filter(User.email == "romain.chaffal@beta.gouv.fr").first()
        suspend_account(user, constants.SuspensionReason.UPON_USER_REQUEST, admin)
        logger.info("[DELETE OR SUSPEND USER FROM FILE] user %s suspended", user_email)
        return
    # 3 no deposit -> delete account
    favorites = Favorite.query.filter(Favorite.userId == user.id).all()
    repository.delete(*favorites)
    repository.delete(user)
    logger.info("[DELETE OR SUSPEND USER FROM FILE] user %s deleted", user_email)
    return


# run("./user_to_delete.csv")
