import pandas
from sqlalchemy import func

from models import Deposit, Booking, Payment
from models.db import db
from models.payment_status import TransactionStatus


def get_total_deposits():
    return db.session.query(
        func.coalesce(
            func.sum(Deposit.amount),
            0
        )
    ).scalar()


def get_total_amount_spent():
    return db.session.query(
        func.coalesce(
            func.sum(Booking.amount * Booking.quantity),
            0
        )
    ) \
        .filter_by(isCancelled=False) \
        .scalar()


def get_total_amount_to_pay():
    return db.session.query(
        func.coalesce(
            func.sum(Payment.amount),
            0
        )
    ) \
        .filter(Payment.currentStatus != TransactionStatus.BANNED) \
        .scalar()


def query_get_top_20_offers_by_number_of_bookings():
    return db.engine.execute(
        """
        SELECT offer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount)
        FROM offer
        JOIN stock ON stock."offerId" = offer.id
        JOIN booking ON booking."stockId" = stock.id
        WHERE booking."isCancelled" IS FALSE
        GROUP BY offer.id, offer.name
        ORDER BY quantity DESC, offer.name ASC
        LIMIT 20;
        """)


def get_top_20_offers_table():
    top_20_offers_by_number_of_bookings = query_get_top_20_offers_by_number_of_bookings().fetchall()
    return pandas.DataFrame(columns = ['Offre', 'Nombre de réservations', 'Montant dépensé'], data = top_20_offers_by_number_of_bookings)


def query_get_top_20_offerers_by_number_of_bookings():
    return db.engine.execute(
        """
        SELECT offerer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount)
        FROM offerer
        JOIN venue ON venue."managingOffererId" = offerer.id
        JOIN offer ON offer."venueId" = venue.id
        JOIN stock ON stock."offerId" = offer.id
        JOIN booking ON booking."stockId" = stock.id
        WHERE booking."isCancelled" IS FALSE
        GROUP BY offerer.id, offerer.name
        ORDER BY quantity DESC, offerer.name ASC
        LIMIT 20;
        """)


def get_top_20_offerers_table():
    top_20_offers_by_number_of_bookings = query_get_top_20_offerers_by_number_of_bookings().fetchall()
    return pandas.DataFrame(columns = ['Structure', 'Nombre de réservations', 'Montant dépensé'], data = top_20_offers_by_number_of_bookings)


# TODO: à tester et adapter - ordonner par montant dépensé
def query_get_top_20_offerers_by_booking_amounts():
    return db.engine.execute(
        """
        SELECT offerer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount) AS booking_amount
        FROM offerer
        JOIN venue ON venue."managingOffererId" = offerer.id
        JOIN offer ON offer."venueId" = venue.id
        JOIN stock ON stock."offerId" = offer.id
        JOIN booking ON booking."stockId" = stock.id
        WHERE booking."isCancelled" IS FALSE
        GROUP BY offerer.id, offerer.name
        ORDER BY booking_amount DESC, offerer.name ASC
        LIMIT 20;
        """)


def get_top_20_offerers_by_amount_table():
    top_20_offers_by_number_of_bookings = query_get_top_20_offerers_by_booking_amounts().fetchall()
    return pandas.DataFrame(columns = ['Structure', 'Nombre de réservations', 'Montant dépensé'], data = top_20_offers_by_number_of_bookings)