"""
Send pre-anonymization email to detached pro accounts which have been inactive for more than 3 years - 30 days.
1433 pro accounts found on staging (2025-06-16).
"""

import argparse
import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from dateutil.relativedelta import relativedelta

# bookings_api not used but avoids circular import
from pcapi.core.bookings import api as bookings_api  # noqa: F401
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Send pre-anonymization email to pro accounts")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    almost_three_years_ago = datetime.date.today() - relativedelta(years=3, days=-30)

    users = (
        users_api._get_anonymize_pro_query(
            sa.or_(
                sa.cast(users_models.User.lastConnectionDate, sa.Date) < almost_three_years_ago,
                sa.and_(
                    users_models.User.lastConnectionDate.is_(None),
                    sa.cast(users_models.User.dateCreated, sa.Date) < almost_three_years_ago,
                ),
            ),
        )
        .options(sa_orm.load_only(users_models.User.email))
        .all()
    )

    print(f"{len(users)} pro accounts found")

    for user in users:
        print(user, user.email)
        if args.not_dry:
            transactional_mails.send_pre_anonymization_email_to_pro(user)

    if not args.not_dry:
        print("Was dry run, use --not-dry to really send emails.")
