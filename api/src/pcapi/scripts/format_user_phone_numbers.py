import argparse
from datetime import datetime
import logging
import os
import warnings

from sqlalchemy.orm import load_only


warnings.filterwarnings("ignore")


LOGGER = logging.getLogger(__name__)


def get_users(from_, to):  # type: ignore [no-untyped-def]
    users = (User.query.options(load_only("id", "phoneNumber")).order_by(User.id))[from_:to]
    return users


def process_users_batch(dry, users):  # type: ignore [no-untyped-def]
    changed = 0
    errors = 0
    none = 0
    ok = 0

    for user in users:
        if user.phoneNumber is None:
            none += 1
            continue

        try:
            if user.phoneNumber == "":
                formatted = None
            else:
                formatted = ParsedPhoneNumber(user.phoneNumber, region="FR").phone_number

        except InvalidPhoneNumber:
            LOGGER.error("invalid phone number %s for user %s", user.phoneNumber, user.id)
            errors += 1

        else:
            if formatted == user.phoneNumber:
                ok += 1

            else:
                changed += 1
                if dry:
                    LOGGER.info(
                        "phone number of user %s will be formatted from %s to %s",
                        user.id,
                        user.phoneNumber,
                        formatted,
                    )
                else:
                    user.phoneNumber = formatted

    return changed, errors, none, ok


def process_users(batch_size, dry):  # type: ignore [no-untyped-def]
    if dry:
        LOGGER.info("DRY RUN")

    from_, to = 0, batch_size
    batch = 1
    total_changed = 0
    total_errors = 0
    total_none = 0
    total_ok = 0

    try:
        while users := get_users(from_, to):
            start = datetime.utcnow()
            LOGGER.info("starting batch #%s of length %s", batch, len(users))

            changed, errors, none, ok = process_users_batch(dry, users)

            if dry:
                LOGGER.info(
                    "%s numbers would have been changed, %s errors, %s None, %s OK",
                    changed,
                    errors,
                    none,
                    ok,
                )
            else:
                db.session.commit()
                LOGGER.info(
                    "%s numbers changed, %s errors, %s None, %s OK (in %s)",
                    changed,
                    errors,
                    none,
                    ok,
                    datetime.utcnow() - start,
                )

            from_ += batch_size
            to += batch_size

            total_changed += changed
            total_errors += errors
            total_none += none
            total_ok += ok

        return total_changed, total_errors, total_none, total_ok

    except KeyboardInterrupt:
        LOGGER.warning("keyboard interrupted")
        return total_changed, total_errors, total_none, total_ok


def main(dry=True, batch_size=1000):  # type: ignore [no-untyped-def]
    with app.app_context():
        start = datetime.utcnow()
        total_changed, total_errors, total_none, total_ok = process_users(batch_size, dry)
        LOGGER.info(
            "totals: %s numbers changed, %s errors, %s None, %s OK (in %s)",
            total_changed,
            total_errors,
            total_none,
            total_ok,
            datetime.utcnow() - start,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="format users phone number in DB")
    parser.add_argument("--batch-size", type=int, default=1000, help="number of users to update in one query")
    parser.add_argument("--not-dry", action="store_true", help="used to really process the formatting")
    parser.add_argument("--local", action="store_true", help="used to run on local machine (for tests)")
    args = parser.parse_args()

    if args.local:
        os.environ["CORS_ALLOWED_ORIGINS"] = ""
        os.environ["CORS_ALLOWED_ORIGINS_BACKOFFICE"] = ""
        os.environ["CORS_ALLOWED_ORIGINS_NATIVE"] = ""
        os.environ["CORS_ALLOWED_ORIGINS_ADAGE_IFRAME"] = ""
        os.environ["DATABASE_URL"] = "postgresql://pass_culture:pass_culture@localhost:5434/pass_culture"

    from pcapi.core.subscription.phone_validation.exceptions import InvalidPhoneNumber
    from pcapi.core.users.models import User
    from pcapi.flask_app import app
    from pcapi.flask_app import db
    from pcapi.utils.phone_number import ParsedPhoneNumber

    main(
        dry=not args.not_dry,
        batch_size=args.batch_size,
    )
