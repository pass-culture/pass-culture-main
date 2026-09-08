"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-43548-bookings \
  -f NAMESPACE=recreate_bookings \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import decimal
import logging

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.core.users.repository import get_and_lock_user
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def recreate_booking(
    original_booking_id: int,
    new_venue_id: int,
    new_offer_id: int,
) -> None:
    original_booking = (
        db.session.query(bookings_models.Booking)
        .filter(bookings_models.Booking.id == original_booking_id)
        .options(sa_orm.joinedload(bookings_models.Booking.user))
        .one()
    )
    beneficiary = original_booking.user

    logger.info(
        "Processing booking",
        extra={
            "booking_id": original_booking_id,
            "token": original_booking.token,
            "venue_id": original_booking.venueId,
            "user_id": beneficiary.id,
            "amount": float(original_booking.total_amount),
        },
    )

    offer = (
        db.session.query(offers_models.Offer)
        .filter_by(id=new_offer_id)
        .options(sa_orm.joinedload(offers_models.Offer.stocks))
        .one()
    )

    logger.info("Found destination offer", extra={"offer_id": new_offer_id, "venue_id": offer.venueId})

    original_is_canceled = original_booking.status == bookings_models.BookingStatus.CANCELLED
    original_is_reimbursed = original_booking.status == bookings_models.BookingStatus.REIMBURSED

    assert original_is_canceled or original_is_reimbursed
    assert len(offer.stocks) >= 1
    assert beneficiary.deposit  # helps mypy

    stock_id = min(offer.stocks, key=lambda s: s.price).id

    stock = offers_repository.get_and_lock_stock(stock_id=stock_id)
    get_and_lock_user(beneficiary.id)
    domains_credit = users_api.get_domains_credit(beneficiary)
    assert domains_credit  # helps mypy
    remaining_credit = domains_credit.all.remaining
    amount = stock.price

    if remaining_credit < amount:
        recredit_amount = amount - remaining_credit + decimal.Decimal("0.00")
        recredit_beneficiary(beneficiary, recredit_amount, original_booking.token)
        domains_credit = users_api.get_domains_credit(beneficiary)
        assert domains_credit  # helps mypy
        remaining_credit = domains_credit.all.remaining
    else:
        recredit_amount = None

    logger.info(
        "Creating new booking by script",
        extra={"user_id": beneficiary.id, "remaining_credit": remaining_credit, "amount": float(amount)},
    )

    booking = bookings_models.Booking(
        userId=beneficiary.id,
        stockId=stock.id,
        amount=amount,
        quantity=1,
        token=bookings_repository.generate_booking_token(),
        venueId=stock.offer.venueId,
        offererId=stock.offer.venue.managingOffererId,
        priceCategoryLabel=(stock.priceCategory.label if stock.priceCategory else None),
        status=bookings_models.BookingStatus.CONFIRMED,
        depositId=beneficiary.deposit.id,
    )

    now = date_utils.get_naive_utc_now()
    booking.dateCreated = now
    booking.cancellationLimitDate = now
    if beneficiary.deposit is not None and beneficiary.deposit_type == finance_models.DepositType.GRANT_17_18:
        recredit_types = [recredit.recreditType for recredit in beneficiary.deposit.recredits]
        if finance_models.RecreditType.RECREDIT_18 in recredit_types:
            booking.usedRecreditType = bookings_models.BookingRecreditType.RECREDIT_18
        elif finance_models.RecreditType.RECREDIT_17 in recredit_types:
            booking.usedRecreditType = bookings_models.BookingRecreditType.RECREDIT_17

    if original_is_canceled:
        booking.mark_as_used(bookings_models.BookingValidationAuthorType.AUTO)
        assert stock.quantity is not None  # helps mypy
        stock.quantity += booking.quantity
        stock.dnBookedQuantity += booking.quantity
        logger.info(
            "Updating dnBookedQuantity after a successful booking",
            extra={
                "booking_id": booking.id,
                "booking_quantity": booking.quantity,
                "stock_dnBookedQuantity": stock.dnBookedQuantity,
            },
        )
        comment = (
            f"PC-43548 - Suite à l'annulation de la réservation {original_booking.token} pour un trop-perçu car retirée "
            f"dans une autre structure, la réservation {booking.token} a été recréée afin de régulariser."
        )
        if recredit_amount:
            comment += (
                f" Ce jeune a été exceptionnellement recrédité de de {format_price(recredit_amount, None)}"
                f" afin que son crédit soit suffisant créer la réservation à {format_price(amount, None)}."
            )
    else:
        booking.cancel_booking(bookings_models.BookingCancellationReasons.FINANCE_INCIDENT)
        comment = (
            f"PC-43548 - Suite au remboursement de la réservation {original_booking.token} retirée dans une autre "
            f"structure, la réservation {booking.token} a été recréée annulée afin de régulariser par geste commercial "
            "sans impact sur le crédit du jeune."
        )

    logger.info(
        "Created booking by script",
        extra={
            "original_token": original_booking.token,
            "original_booking_id": original_booking.id,
            "original_amount": original_booking.amount,
            "original_venue_id": original_booking.venueId,
            "offer_id": new_offer_id,
            "stock_id": stock.id,
            "token": booking.token,
            "booking_id": booking.id,
            "status": booking.status,
            "amount": float(booking.amount),
        },
    )
    logger.info(comment)  # for tracking in dry-run mode

    action = history_api.add_action(history_models.ActionType.COMMENT, author=None, user=beneficiary, comment=comment)
    db.session.add_all((booking, stock, action))
    db.session.flush()  # to setup relations on `booking` for `add_event()` below.

    if original_is_canceled:
        finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED,
            booking=booking,
        )

    update_external_user(booking.user)


def recredit_beneficiary(beneficiary: users_models.User, amount: decimal.Decimal, token: str) -> None:
    """
    Only one reimbursed booking concerned (see Notion).
    PC-38491 fixing get_deposit_balance must have been deployed before running this script.
    """
    deposit = beneficiary.deposit
    assert deposit

    db.session.add(
        finance_models.Recredit(
            deposit=deposit,
            amount=amount,
            recreditType=finance_models.RecreditType.MANUAL_MODIFICATION,
            comment=(
                "PC-43548 - Recrédit exceptionnel suite au retrait d'une réservation dans une autre structure afin "
                f" de rembourser cette dernière, en doublon d'une réservation {token} déjà remboursée (support pro)"
            ),
        )
    )
    deposit.amount += amount
    db.session.add(deposit)
    db.session.flush()

    assert beneficiary.deposit  # helps mypy
    balance = db.session.query(sa.func.get_deposit_balance(beneficiary.deposit.id, False)).scalar()
    logger.info(
        "Exceptional recredit", extra={"user_id": beneficiary.id, "amount": float(amount), "deposit_balance": balance}
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--booking-id", type=int, required=True)
    parser.add_argument("--new-venue-id", type=int, required=True)
    parser.add_argument("--new-offer-id", type=int, required=True)
    args = parser.parse_args()

    recreate_booking(
        original_booking_id=args.booking_id,
        new_venue_id=args.new_venue_id,
        new_offer_id=args.new_offer_id,
    )

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
