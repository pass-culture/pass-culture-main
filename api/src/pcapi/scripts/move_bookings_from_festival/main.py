import argparse

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.models as offers_models
from pcapi.flask_app import app
from pcapi.models import db


OFFER_EQUIVALENCE_LIST = {
    "BILLET JOUR - VEN 27": {"old_offer_id": 273920933, "new_offer_id": 289074757},
    "BILLET JOUR - SAM 28": {"old_offer_id": 273921336, "new_offer_id": 289075714},
    "BILLET JOUR - DIM 29": {"old_offer_id": 273921579, "new_offer_id": 289076714},
    "PASS 2 JOURS - SAM 28 + DIM 29": {
        "old_offer_id": 273915284,
        "new_offer_id": 289078111,
    },
    "PASS 2 JOURS - VEN 27 + SAM 28": {
        "old_offer_id": 273915257,
        "new_offer_id": 289077254,
    },
    "PASS 2 JOURS - VEN 27 + DIM 29": {
        "old_offer_id": 273915160,
        "new_offer_id": 289077384,
    },
    "PASS 3 JOURS": {"old_offer_id": 273914958, "new_offer_id": 289078131},
}


def move_bookings_from_one_siren_to_another(old_offer_id: int, new_offer_id: int) -> None:
    new_stock = offers_models.Stock.query.filter(
        offers_models.Stock.isSoftDeleted.is_(False),
        offers_models.Stock.offerId == new_offer_id,
    ).one()
    old_stock = offers_models.Stock.query.filter(
        offers_models.Stock.isSoftDeleted.is_(False),
        offers_models.Stock.offerId == old_offer_id,
    ).one()
    print(f"old_stock had {old_stock.dnBookedQuantity} bookings, new stock has {new_stock.dnBookedQuantity}")
    for booking in old_stock.bookings:
        if booking.status == bookings_models.BookingStatus.CONFIRMED:
            booking.venueId = new_stock.offer.venueId
            booking.offererId = new_stock.offer.venue.managingOffererId
            booking.stockId = new_stock.id
            db.session.add(booking)
            db.session.flush()
    bookings_api.recompute_dnBookedQuantity([old_stock.id, new_stock.id])
    db.session.flush()
    print(f"new stock should have {new_stock.dnBookedQuantity} bookings now")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--not-dry",
        action="store_true",
        help="set to really process (dry-run by default)",
    )
    args = parser.parse_args()

    for offer_dict in OFFER_EQUIVALENCE_LIST.values():
        move_bookings_from_one_siren_to_another(offer_dict["old_offer_id"], offer_dict["new_offer_id"])

    if args.not_dry:
        db.session.commit()
    else:
        db.session.rollback()
