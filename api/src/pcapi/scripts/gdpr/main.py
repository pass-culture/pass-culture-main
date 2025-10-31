import argparse
from datetime import datetime

from pcapi.app import app
from pcapi.core.users.gdpr_api import anonymize_user
from pcapi.core.users.models import User
from pcapi.models import db


# do not reuse, this script is only godd for a specific case.(only one deposit, no bookings)


def main(user_id: int, author_id: int) -> None:
    author = User.query.get(author_id)
    user = User.query.get(user_id)
    if user:
        assert len(user.deposits) <= 1
        for deposit in user.deposits:
            deposit.expirationDate = datetime.utcnow()
        db.session.flush()
        anonymize_user(user, author=author)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("user_id", type=int)
    parser.add_argument("author_id", type=int)
    args = parser.parse_args()

    main(args.user_id, args.author_id)

    db.session.commit()
