import sqlalchemy as sa

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


def get_all_bookings_by_offer_id(offer_id: int) -> list[bookings_models.Booking]:
    bookings = (
        bookings_models.Booking.query.filter(
            offers_models.Stock.offerId == offer_id,
            sa.or_(
                bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
                bookings_models.Booking.status == bookings_models.BookingStatus.USED,
            ),
        )
        .join(offers_models.Stock)
        .all()
    )
    print(f"{len(bookings)} bookings to update")
    return bookings


def transpose_booking_to_other_stock(bookings: list[bookings_models.Booking], new_offer_id: int) -> None:
    new_stock = offers_models.Stock.query.filter(offers_models.Stock.offerId == new_offer_id).one()
    if bookings:
        for booking in bookings:
            booking.stockId = new_stock.id
            db.session.add(booking)
    else:
        print("No booking to update")
    db.session.commit()


def delete_pricings(bookings: list[bookings_models.Booking]) -> None:
    booking_ids = [booking.id for booking in bookings]
    pricings_to_delete = finance_models.Pricing.query.filter(
        finance_models.Pricing.bookingId.in_(booking_ids),
        finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
    ).all()

    pricing_ids = [pricing.id for pricing in pricings_to_delete]
    print(f"{len(pricing_ids)} pricings to delete")

    finance_models.PricingLine.query.filter(
        finance_models.PricingLine.pricingId.in_(pricing_ids),
    ).delete(synchronize_session=False)

    finance_models.Pricing.query.filter(
        finance_models.Pricing.bookingId.in_(booking_ids),
        finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
    ).delete(synchronize_session=False)


def recompute_stocks(offer_ids: list[int]) -> None:
    stock_ids = (
        offers_models.Stock.query.with_entities(offers_models.Stock.id)
        .filter(offers_models.Stock.offerId.in_(offer_ids))
        .all()
    )
    real_stock_ids = [id_tuple[0] for id_tuple in stock_ids]
    bookings_api.recompute_dnBookedQuantity(real_stock_ids)


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        print("Starting update")

        print("Running booking batch: from offer 85196182 to offer 88008609")
        bookings_from_85196182 = get_all_bookings_by_offer_id(85196182)
        delete_pricings(bookings_from_85196182)
        transpose_booking_to_other_stock(bookings_from_85196182, 88008609)

        print("Running booking batch: from offer 86272276 to offer 88238154")
        bookings_from_86272276 = get_all_bookings_by_offer_id(86272276)
        delete_pricings(bookings_from_86272276)
        transpose_booking_to_other_stock(bookings_from_86272276, 88238154)

        print("Running booking batch: from offer 87857886 to offer 88238421")
        bookings_from_87857886 = get_all_bookings_by_offer_id(87857886)
        delete_pricings(bookings_from_87857886)
        transpose_booking_to_other_stock(bookings_from_87857886, 88238421)

        print("Running booking batch: from offer 85429867 to offer 88238485")
        bookings_from_85429867 = get_all_bookings_by_offer_id(85429867)
        delete_pricings(bookings_from_85429867)
        transpose_booking_to_other_stock(bookings_from_85429867, 88238485)

        recompute_stocks(
            [
                85196182,
                88008609,
                86272276,
                88238154,
                87857886,
                88238421,
                85429867,
                88238485,
            ]
        )

        print("Update complete")
