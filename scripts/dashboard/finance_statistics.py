from pprint import pprint

import pandas
from sqlalchemy import func, text

from models import Deposit, Booking, Payment, User, Stock, Offer, Venue
from models.db import db
from models.payment_status import TransactionStatus


def get_total_deposits(departement_code=None):
    query = db.session.query(func.coalesce(func.sum(Deposit.amount), 0))

    if departement_code:
        query = query.join(User).filter(User.departementCode == departement_code)

    return query.scalar()


def get_total_amount_spent(departement_code=None):
    query = db.session.query(func.coalesce(func.sum(Booking.amount * Booking.quantity), 0))

    if departement_code:
        query = query.join(User).filter(User.departementCode == departement_code)

    return query \
        .filter(Booking.isCancelled == False) \
        .scalar()


def get_total_amount_to_pay(departement_code=None):
    query = db.session.query(func.coalesce(func.sum(Payment.amount), 0)) \
        .filter(Payment.currentStatus != TransactionStatus.BANNED)

    if departement_code:
        query = query.join(Booking) \
            .join(Stock) \
            .join(Offer) \
            .join(Venue) \
            .filter(Venue.departementCode == departement_code)

    return query \
        .scalar()


def get_top_20_offers_table(departement_code=None):
    top_20_offers_by_number_of_bookings = _query_get_top_20_offers_by_number_of_bookings(departement_code)
    return pandas.DataFrame(columns=['Offre', 'Nombre de réservations', 'Montant dépensé'],
                            data=top_20_offers_by_number_of_bookings)


def get_top_20_offerers_table_by_number_of_bookings():
    top_20_offers_by_number_of_bookings = _query_get_top_20_offerers_by_number_of_bookings()
    return pandas.DataFrame(columns=['Structure', 'Nombre de réservations', 'Montant dépensé'],
                            data=top_20_offers_by_number_of_bookings)


def get_top_20_offerers_by_amount_table():
    top_20_offers_by_number_of_bookings = _query_get_top_20_offerers_by_booking_amounts()
    return pandas.DataFrame(columns=['Structure', 'Nombre de réservations', 'Montant dépensé'],
                            data=top_20_offers_by_number_of_bookings)


def get_not_cancelled_bookings_by_departement():
    non_cancelled_booking_by_department = _query_non_cancelled_bookings_by_departement()
    return pandas.DataFrame(columns=['Departement', 'Nombre de réservations'],
                            data=non_cancelled_booking_by_department)


def _query_get_top_20_offers_by_number_of_bookings(departement_code=None):
    if departement_code:
        query = text("""
            SELECT offer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount)
            FROM offer
            JOIN stock ON stock."offerId" = offer.id
            JOIN booking ON booking."stockId" = stock.id
            JOIN venue ON offer."venueId" = venue.id
            WHERE booking."isCancelled" IS FALSE
            AND venue."departementCode" = :departementCode
            GROUP BY offer.id, offer.name
            ORDER BY quantity DESC, offer.name ASC
            LIMIT 20;
            """).bindparams(departementCode=departement_code)
    else:
        query = text("""
            SELECT offer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount)
            FROM offer
            JOIN stock ON stock."offerId" = offer.id
            JOIN booking ON booking."stockId" = stock.id
            WHERE booking."isCancelled" IS FALSE
            GROUP BY offer.id, offer.name
            ORDER BY quantity DESC, offer.name ASC
            LIMIT 20;
            """)

    return db.engine.execute(query).fetchall()


def _query_non_cancelled_bookings_by_departement():
    return db.engine.execute(
        """
        SELECT "departementCode", COUNT(*) as "nb_bookings" 
        FROM booking
        JOIN "user" ON "user".id = booking."userId"
        WHERE booking."isCancelled" IS FALSE
        GROUP BY "user"."departementCode"
        ORDER BY "user"."departementCode";
        """).fetchall()


def _query_get_top_20_offerers_by_number_of_bookings():
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
        """).fetchall()


def _query_get_top_20_offerers_by_booking_amounts():
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
        """).fetchall()
