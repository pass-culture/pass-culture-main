import argparse
import time
import traceback

import sqlalchemy.orm as sa_orm

from pcapi.core import mails as mails_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils.requests import ExternalAPIException


def delete_external_suspended_users(min_id: int = 0, do_update: bool = False) -> None:
    users = (
        db.session.query(users_models.User)
        .outerjoin(offerers_models.Venue, offerers_models.Venue.bookingEmail == users_models.User.email)
        .filter(
            users_models.User.id >= min_id,
            users_models.User.isActive.is_(False),
            offerers_models.Venue.id.is_(None),
        )
        .order_by(users_models.User.id)
        .options(
            sa_orm.load_only(
                users_models.User.id, users_models.User.email, users_models.User.roles, users_models.User.dateCreated
            )
        )
        .all()
    )

    print(len(users), "users found")

    for user in users:
        print(f"Delete external user {user.id} {user.email} {user.roles} created on {user.dateCreated.isoformat()}")
        if do_update:
            if not user.isActive:
                retries = 3
                try:
                    mails_api.delete_contact(user.email, user.has_any_pro_role)
                except ExternalAPIException:
                    retries -= 1
                    if retries == 0:
                        raise
                    print(traceback.format_exc())
                    time.sleep(10)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Delete external contact for suspended users")
    parser.add_argument("--min-id", type=int, default=0, help="minimum user id (for resume)")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    delete_external_suspended_users(min_id=args.min_id, do_update=args.not_dry)
