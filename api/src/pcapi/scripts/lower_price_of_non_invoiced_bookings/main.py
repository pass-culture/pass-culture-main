import argparse
import decimal
import logging

# pylint: disable=unused-import
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import _delete_dependent_pricings
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def _get_all_bookings_by_offer_id(offer_id: int) -> list[bookings_models.Booking]:
    bookings = (
        bookings_models.Booking.query.filter(
            offers_models.Stock.offerId == offer_id,
            bookings_models.Booking.status == bookings_models.BookingStatus.USED,
        )
        .join(offers_models.Stock)
        .all()
    )
    logger.info("PC-29902 : %s bookings to update", len(bookings))
    return bookings


def _give_new_price_to_bookings(bookings: list[bookings_models.Booking], new_price: decimal.Decimal) -> None:
    for booking in bookings:
        booking.amount = new_price
        db.session.add(booking)
    db.session.flush()


def _delete_pricings(booking_ids: list[int]) -> None:
    pricings_to_delete = finance_models.Pricing.query.filter(
        finance_models.Pricing.bookingId.in_(booking_ids),
        finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
    ).all()
    pricing_ids = [pricing.id for pricing in pricings_to_delete]
    logger.info("PC-29902 : %s pricings to delete", len(pricing_ids))
    finance_models.PricingLine.query.filter(
        finance_models.PricingLine.pricingId.in_(pricing_ids),
    ).delete(synchronize_session=False)
    finance_models.Pricing.query.filter(
        finance_models.Pricing.bookingId.in_(booking_ids),
        finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
    ).delete(synchronize_session=False)
    db.session.flush()


def _reinit_finance_events(booking_ids: list[int]) -> None:
    finance_events = finance_models.FinanceEvent.query.filter(
        finance_models.FinanceEvent.bookingId.in_(booking_ids),
        finance_models.FinanceEvent.status == finance_models.FinanceEventStatus.PRICED,
    ).all()
    for event in finance_events:
        event.status = finance_models.FinanceEventStatus.READY
        db.session.add(event)
        _delete_dependent_pricings(
            event, "PC-29902 : redo pricings of festival with cancelled days"
        )  # just to be sure, although the whole festival is under a custom reimbursement rule
    db.session.flush()


def change_price_of_bookings_from_offer(offer_id: int, new_price: decimal.Decimal) -> None:
    logger.info("PC-29902 : Update offer %s to new price %s", offer_id, new_price)
    bookings = _get_all_bookings_by_offer_id(offer_id)
    booking_ids = [booking.id for booking in bookings]
    _delete_pricings(booking_ids)
    _reinit_finance_events(booking_ids)
    _give_new_price_to_bookings(bookings, new_price)


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        logger.info("PC-29902 : Starting update")

        parser = argparse.ArgumentParser(description="Modify price of bookings")
        parser.add_argument(
            "--not-dry",
            action="store_true",
            help="set to really process (dry-run by default)",
        )
        args = parser.parse_args()

        # P2N#24 - Forfait 3 jours
        change_price_of_bookings_from_offer(104077642, decimal.Decimal("41.67"))
        # P2N#24 - Forfait 2 jours Ven-Sam
        change_price_of_bookings_from_offer(104077682, decimal.Decimal("47.00"))
        # P2N#24 - Billet combiné 3 jours
        change_price_of_bookings_from_offer(104077753, decimal.Decimal("52.00"))
        # Forfait 3 jours (offre de rattrapage)
        change_price_of_bookings_from_offer(168016972, decimal.Decimal("41.67"))

        if args.not_dry:
            db.session.commit()
        else:
            db.session.rollback()

        logger.info("PC-29902 : Update complete")
