import argparse
from datetime import datetime
import logging

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Deposit
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()


def update_external_users(start_id: int = 0, bach_size: int = 1000) -> None:
    query = (
        User.query.join(Deposit)
        .filter(
            Deposit.expirationDate > datetime.utcnow(),
            User.isActive.is_(True),
        )
        .order_by(User.id.desc())
    )

    max_id = query.first().id

    while start_id <= max_id:
        users = query.filter(User.id >= start_id, User.id < start_id + bach_size).all()
        for user in users:
            update_external_user(user)
        start_id += bach_size
        logger.info("Updated users up to %s excluded", start_id)


if __name__ == "__main__":
    # https://github.com/pass-culture/pass-culture-main/blob/pc-34961/api/src/pcapi/scripts/update_external_users/main.py
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--start-id", type=int, default=0)
    args = parser.parse_args()

    update_external_users(args.start_id, args.batch_size)

    logger.info("Finished")
    db.session.commit()
