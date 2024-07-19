import argparse
import secrets

# pylint: disable=unused-import
from pcapi.core.bookings import api as bookings_api
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.users import api as users_api
from pcapi.core.users import constants
from pcapi.core.users import models as users_models
from pcapi.models import db


def run_password_reset(ids: list[int]) -> None:
    users = users_models.User.query.filter(users_models.User.id.in_(ids))

    for user in users:
        user.setPassword(secrets.token_urlsafe())
        db.session.add(user)
        token = users_api.create_reset_password_token(user)
        transactional_mails.send_reset_password_email_to_user(token, constants.SuspensionReason.FRAUD_HACK)

    db.session.commit()


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        print("Starting script")
        parser = argparse.ArgumentParser(description="Reset users' passwords")
        parser.add_argument("--user-ids", type=str, default=0, help="User ids, separated by a comma")
        args = parser.parse_args()
        user_ids = [int(user_id) for user_id in set(args.user_ids.split(","))]
        run_password_reset(user_ids)
        print("Script done")
