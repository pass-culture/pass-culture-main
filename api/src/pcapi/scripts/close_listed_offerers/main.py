"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37351-close-all-now-forbidden-offerers/api/src/pcapi/scripts/close_listed_offerers/main.py

"""

import argparse
import csv
import logging
import os
import typing
from datetime import date

from dateutil.relativedelta import relativedelta

import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
from pcapi.app import app
from pcapi.core import mails
from pcapi.core import search
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import validation as bookings_validation
from pcapi.core.categories import subcategories
from pcapi.core.educational import repository as educational_repository
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails import models as mails_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerer_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import repository as users_repository
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import date as date_utils
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


# Adapted mail functions for pro mail
def get_offerer_closed_email_data(offerer: offerers_models.Offerer) -> mails_models.TransactionalEmailData:
    bookings_subcategory_ids = [
        entities[0]
        for entities in (
            db.session.query(bookings_models.Booking)
            .filter(
                bookings_models.Booking.offererId == offerer.id,
                bookings_models.Booking.status.in_(
                    [bookings_models.BookingStatus.CONFIRMED, bookings_models.BookingStatus.USED]
                ),
            )
            .join(bookings_models.Booking.stock)
            .join(offers_models.Stock.offer)
            .with_entities(offers_models.Offer.subcategoryId)
            .distinct()
        ).all()
    ]

    has_thing_bookings = False
    has_event_bookings = False

    for subcategory_id in bookings_subcategory_ids:
        subcategory = subcategories.ALL_SUBCATEGORIES_DICT.get(subcategory_id)
        if subcategory and subcategory.is_event:
            has_event_bookings = True
        else:
            has_thing_bookings = True

    if not has_event_bookings:
        has_event_bookings = educational_repository.offerer_has_ongoing_collective_bookings(
            offerer.id, include_used=True
        )

    return mails_models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_CLOSED_MANUALLY.value,
        params={
            "IS_ESCAPE_GAME": True,
            "OFFERER_NAME": offerer.name,
            "SIREN": offerer.siren,
            "END_DATE": get_date_formatted_for_email(date.today()),
            "HAS_THING_BOOKINGS": has_thing_bookings,
            "HAS_EVENT_BOOKINGS": has_event_bookings,
        },
    )


def send_offerer_closed_specific_email_to_pro(offerer: offerers_models.Offerer) -> None:
    pro_users = users_repository.get_users_with_validated_attachment(offerer)
    data = get_offerer_closed_email_data(offerer)
    for pro_user in pro_users:
        mails.send(recipients=[pro_user.email], data=data)


# Adapted mail functions for beneficiary mail
def get_booking_cancellation_by_pro_to_beneficiary_email_data(
    booking: bookings_models.Booking,
) -> mails_models.TransactionalEmailData:
    stock = booking.stock
    offer = stock.offer
    beneficiary = booking.user

    if offer.isEvent:
        event_date = get_date_formatted_for_email(get_event_datetime(stock))
        event_hour = get_time_formatted_for_email(get_event_datetime(stock))
    else:
        event_date = None
        event_hour = None

    is_free_offer = stock.price == 0

    return mails_models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value,
        params={
            "BOOKING_CONTACT": offer.bookingContact,
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "FORMATTED_PRICE": format_price(booking.total_amount, beneficiary),
            "IS_EVENT": offer.isEvent,
            "IS_FREE_OFFER": is_free_offer,
            "IS_ONLINE": offer.hasUrl,
            "IS_THING": not offer.hasUrl and offer.isThing,
            "IS_EXTERNAL": booking.isExternal,
            "OFFER_NAME": offer.name,
            "OFFER_PRICE": booking.total_amount,
            "OFFERER_NAME": offer.venue.managingOfferer.name,
            "REASON": None,  # We have reason, but we want to have the rejected-by-fraud-version of the template
            "REJECTED": True,
            "USER_FIRST_NAME": booking.firstName,
            "USER_LAST_NAME": booking.lastName,
            "VENUE_NAME": offer.venue.common_name,
        },
    )


def send_specific_cancellation_by_pro_to_beneficiary_email(booking: bookings_models.Booking) -> None:
    data = get_booking_cancellation_by_pro_to_beneficiary_email_data(booking)
    mails.send(recipients=[booking.email], data=data)


def cancel_booking_on_closed_offerer(booking: bookings_models.Booking, author_id: int | None = None) -> None:
    bookings_validation.check_booking_can_be_cancelled(booking)
    try:
        cancelled = bookings_api._cancel_booking(
            booking, bookings_models.BookingCancellationReasons.OFFERER_CLOSED, author_id=author_id
        )
    except external_bookings_exceptions.ExternalBookingException as exc:
        logger.info(
            "API error while cancelling external booking, try to cancel unilaterally",
            extra={"exc": exc, "booking": booking.id},
        )
        cancelled = bookings_api._cancel_booking(
            booking,
            bookings_models.BookingCancellationReasons.OFFERER_CLOSED,
            one_side_cancellation=True,
            author_id=author_id,
        )
    if not cancelled:
        return
    logger.info("Cancelled booking on closed offerer", extra={"booking": booking.id})

    # Only send mail if user has an unexpired deposit, or one that has expired less than 3 months ago
    user_deposit = booking.user.deposit
    assert user_deposit  # helps mypy
    if user_deposit.expirationDate and user_deposit.expirationDate > date_utils.get_naive_utc_now() - relativedelta(
        months=3
    ):
        send_specific_cancellation_by_pro_to_beneficiary_email(booking)


# Same as in offerers/api.py
def _cancel_individual_bookings_on_offerer_closure(offerer_id: int, author_id: int | None) -> None:
    bookings = offerers_api.get_individual_bookings_to_cancel_on_offerer_closure(offerer_id)

    for booking in bookings:
        with atomic():
            try:
                cancel_booking_on_closed_offerer(booking, author_id=author_id)
            except Exception as exc:
                mark_transaction_as_invalid()
                logger.exception(
                    "Failed to cancel booking when closing offerer",
                    extra={"exc": exc, "booking_id": booking.id, "offerer_id": offerer_id},
                )

    db.session.flush()


def close_offerer(
    offerer: offerers_models.Offerer,
    **action_args: typing.Any,
) -> None:
    if offerer.isClosed:
        raise offerer_exceptions.OffererAlreadyClosedException()

    offerer.validationStatus = ValidationStatus.CLOSED
    db.session.add(offerer)
    history_api.add_action(
        history_models.ActionType.OFFERER_CLOSED,
        author=None,
        offerer=offerer,
        closure_date=date.today().isoformat(),
        comment="Entité juridique d'escape games fermée - PC-37351",
        **action_args,
    )

    applicants = users_repository.get_users_with_validated_attachment(offerer)
    offerers_api.remove_pro_role_and_add_non_attached_pro_role(applicants)

    if applicants:
        send_offerer_closed_specific_email_to_pro(offerer)

    db.session.flush()

    author_id = None

    _cancel_individual_bookings_on_offerer_closure(offerer.id, author_id)
    offerers_api._cancel_collective_bookings_on_offerer_closure(offerer.id, author_id)

    offerers_api._update_external_offerer(offerer, index_with_reason=search.IndexationReason.OFFERER_DEACTIVATION)


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def main(filename: str) -> None:
    rows = _read_csv_file(filename)
    logger.info("Reading file %s", filename)
    offerer_ids = {int(row["offerer_id"]) for row in rows}
    offerers = db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id.in_(offerer_ids)).all()
    for offerer in offerers:
        if not offerer.isValidated:
            logger.info("Offerer {id} is not validated".format(id=offerer.id))
        else:
            try:
                close_offerer(offerer)
            except offerer_exceptions.OffererAlreadyClosedException:
                logger.info("Offerer {id} is already closed".format(id=offerer.id))


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main("offerer_ids")

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
