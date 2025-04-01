import argparse

from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import get_pricing_ordering_date
from pcapi.models import db


COLLECTIVE_BOOKING_ID = 550812
NEW_VENUE_ID = 141330


def move_things() -> None:
    finance_event = finance_models.FinanceEvent.query.filter(
        finance_models.FinanceEvent.collectiveBookingId == COLLECTIVE_BOOKING_ID
    ).one()

    pricing = finance_event.pricings[0]  # only one pricing
    finance_models.PricingLine.query.filter(finance_models.PricingLine.pricingId == pricing.id).delete(
        synchronize_session=False
    )
    finance_models.PricingLog.query.filter(finance_models.PricingLine.pricingId == pricing.id).delete(
        synchronize_session=False
    )
    finance_models.Pricing.query.filter(finance_models.Pricing.id == pricing.id).delete(synchronize_session=False)

    collective_booking = finance_event.collectiveBooking
    finance_event.status = finance_models.FinanceEventStatus.READY
    finance_event.venueId = NEW_VENUE_ID
    finance_event.pricingOrderingDate = get_pricing_ordering_date(collective_booking)

    collective_booking.venueId = NEW_VENUE_ID

    collective_offer = collective_booking.collectiveStock.collectiveOffer
    collective_offer.venueId = NEW_VENUE_ID

    db.session.add(finance_event)
    db.session.add(collective_booking)
    db.session.add(collective_offer)


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        print("Starting update")

        parser = argparse.ArgumentParser(description="Move Used collective booking")
        parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
        args = parser.parse_args()

        move_things()

        if args.not_dry:
            db.session.commit()
        else:
            db.session.rollback()

        print("Update complete")
