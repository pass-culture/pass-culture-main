import argparse
from datetime import datetime

from pcapi.app import app
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.users.api import anonymize_user
from pcapi.core.users.models import User
from pcapi.models import db


def main(user_id: int, author_id: int) -> None:
    author = User.query.get(author_id)
    user = User.query.get(user_id)
    if user:
        assert len(user.deposits) <= 1
        for deposit in user.deposits:
            deposit.expirationDate = datetime.utcnow()
        db.session.flush()
        for booking in user.userBookings:
            try:
                booking.cancel_booking(BookingCancellationReasons.BENEFICIARY, author_id=author_id)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        db.session.flush()
        anonymize_user(user, author=author, force=True)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("user_id", type=int)
    parser.add_argument("author_id", type=int)
    args = parser.parse_args()

    main(args.user_id, args.author_id)

    db.session.commit()
