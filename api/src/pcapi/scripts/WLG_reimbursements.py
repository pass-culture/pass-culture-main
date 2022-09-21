import csv

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models
from pcapi.models import db


SAT_ONLY_OFFER_ID = 52666879
THU_SAT_OFFER_ID = 54523766
SAT_SUN_OFFER_ID = 54595830


def get_bookings_to_reimburse(user_emails, offers_ids):
    return (
        db.session.query(bookings_models.Booking)
        .join(offers_models.Stock, bookings_models.Booking.stock)
        .join(users_models.User, bookings_models.Booking.user)
        .filter(offers_models.Stock.offerId.in_(offers_ids))
        .filter(bookings_models.Booking.status == bookings_models.BookingStatus.USED)
        .filter(users_models.User.email.in_(user_emails))
    )


def reimburse_saturday_only(email_file_path: str, dry_run=True):
    user_emails = get_users_email(email_file_path)
    bookings = get_bookings_to_reimburse(user_emails, [SAT_ONLY_OFFER_ID])
    users_reimbursed = []
    print(f"{len(bookings.count())} bookings eligible for reimbursement.")

    for booking in bookings:
        if not dry_run:
            bookings_api.mark_as_cancelled(booking)
        users_reimbursed.append(booking.user.email)
    print(f"Reimbursement done for users :")

    for user in users_reimbursed:
        print(user.email)


def get_users_email(csv_path: str) -> list[str]:
    with open(csv_path, mode="r", encoding="utf-8"):
        csv_reader = csv.DictReader(csv_path)
        return [row["email"] for row in csv_reader]
