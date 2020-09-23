from typing import List, Tuple

import pandas
from sqlalchemy import func, text

from models import Deposit, BookingSQLEntity, Payment, UserSQLEntity, StockSQLEntity, OfferSQLEntity, VenueSQLEntity
from models.db import db
from models.payment_status import TransactionStatus


def get_total_deposits(departement_code: str = None) -> float:
    query = db.session.query(func.coalesce(func.sum(Deposit.amount), 0))

    if departement_code:
        query = query.join(UserSQLEntity).filter(UserSQLEntity.departementCode == departement_code)

    return float(query.scalar())


def get_total_amount_spent(departement_code: str = None) -> float:
    query = db.session.query(func.coalesce(func.sum(BookingSQLEntity.amount * BookingSQLEntity.quantity), 0))

    if departement_code:
        query = query.join(UserSQLEntity).filter(UserSQLEntity.departementCode == departement_code)

    return float(query \
                 .filter(BookingSQLEntity.isCancelled == False) \
                 .scalar())


def get_total_amount_to_pay(departement_code: str = None) -> float:
    query = db.session.query(func.coalesce(func.sum(Payment.amount), 0)) \
        .filter(Payment.currentStatus != TransactionStatus.BANNED)

    if departement_code:
        query = query.join(BookingSQLEntity) \
            .join(StockSQLEntity) \
            .join(OfferSQLEntity) \
            .join(VenueSQLEntity) \
            .join(UserSQLEntity, UserSQLEntity.id == BookingSQLEntity.userId) \
            .filter(UserSQLEntity.departementCode == departement_code)

    return float(query \
                 .scalar())


def get_top_20_offers_table(departement_code: str = None) -> pandas.DataFrame:
    top_20_offers_by_number_of_bookings = _query_get_top_20_offers_by_number_of_bookings(departement_code)
    return pandas.DataFrame(columns=['Offre', 'Nombre de réservations', 'Montant dépensé'],
                            data=top_20_offers_by_number_of_bookings)


def get_top_20_offerers_table_by_number_of_bookings(departement_code: str = None) -> pandas.DataFrame:
    top_20_offers_by_number_of_bookings = _query_get_top_20_offerers_by_number_of_bookings(departement_code)
    return pandas.DataFrame(columns=['Structure', 'Nombre de réservations', 'Montant dépensé'],
                            data=top_20_offers_by_number_of_bookings)


def get_top_20_offerers_by_amount_table(departement_code: str = None) -> pandas.DataFrame:
    top_20_offers_by_number_of_bookings = _query_get_top_20_offerers_by_booking_amounts(departement_code)
    return pandas.DataFrame(columns=['Structure', 'Nombre de réservations', 'Montant dépensé'],
                            data=top_20_offers_by_number_of_bookings)


def _query_get_top_20_offers_by_number_of_bookings(departement_code: str = None) -> List[Tuple[str, int, float]]:
    if departement_code:
        query = text("""
            SELECT offer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount)
            FROM offer
            JOIN stock ON stock."offerId" = offer.id
            JOIN booking ON booking."stockId" = stock.id
            JOIN "user" ON "user".id = booking."userId"
            WHERE booking."isCancelled" IS FALSE
             AND "user"."departementCode" = :departementCode
             AND offer.type != 'ThingType.ACTIVATION'
             AND offer.type != 'EventType.ACTIVATION'
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
             AND offer.type != 'ThingType.ACTIVATION'
             AND offer.type != 'EventType.ACTIVATION'
            GROUP BY offer.id, offer.name
            ORDER BY quantity DESC, offer.name ASC
            LIMIT 20;
            """)

    return db.engine.execute(query).fetchall()


def _query_get_top_20_offerers_by_number_of_bookings(departement_code: str = None) -> List[Tuple[str, int, float]]:
    if departement_code:
        query = text("""
            SELECT offerer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount)
            FROM offerer
            JOIN venue ON offerer.id = venue."managingOffererId"
            JOIN offer ON offer."venueId" = venue.id
            JOIN stock ON stock."offerId" = offer.id
            JOIN booking ON booking."stockId" = stock.id
            JOIN "user" ON "user".id = booking."userId"
            WHERE booking."isCancelled" IS FALSE
             AND "user"."departementCode" = :departementCode
             AND offer.type != 'ThingType.ACTIVATION'
             AND offer.type != 'EventType.ACTIVATION'
            GROUP BY offerer.id, offerer.name
            ORDER BY quantity DESC, offerer.name ASC
            LIMIT 20;
            """).bindparams(departementCode=departement_code)
    else:
        query = """
            SELECT offerer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount)
            FROM offerer
            JOIN venue ON venue."managingOffererId" = offerer.id
            JOIN offer ON offer."venueId" = venue.id
            JOIN stock ON stock."offerId" = offer.id
            JOIN booking ON booking."stockId" = stock.id
            WHERE booking."isCancelled" IS FALSE
             AND offer.type != 'ThingType.ACTIVATION'
             AND offer.type != 'EventType.ACTIVATION'
            GROUP BY offerer.id, offerer.name
            ORDER BY quantity DESC, offerer.name ASC
            LIMIT 20;
            """

    return db.engine.execute(query).fetchall()


def _query_get_top_20_offerers_by_booking_amounts(departement_code: str = None) -> List[Tuple[str, int, float]]:
    if departement_code:
        query = text("""
            SELECT offerer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount) AS booking_amount
            FROM offerer
            JOIN venue ON venue."managingOffererId" = offerer.id
            JOIN offer ON offer."venueId" = venue.id
            JOIN stock ON stock."offerId" = offer.id
            JOIN booking ON booking."stockId" = stock.id
            JOIN "user" ON booking."userId" = "user".id
            WHERE booking."isCancelled" IS FALSE
             AND "user"."departementCode" = :departementCode
             AND offer.type != 'ThingType.ACTIVATION'
             AND offer.type != 'EventType.ACTIVATION'
            GROUP BY offerer.id, offerer.name
            ORDER BY booking_amount DESC, offerer.name ASC
            LIMIT 20;
            """).bindparams(departementCode=departement_code)
    else:
        query = """
        SELECT offerer.name, SUM(booking.quantity) AS quantity, SUM(booking.quantity * booking.amount) AS booking_amount
        FROM offerer
        JOIN venue ON venue."managingOffererId" = offerer.id
        JOIN offer ON offer."venueId" = venue.id
        JOIN stock ON stock."offerId" = offer.id
        JOIN booking ON booking."stockId" = stock.id
        WHERE booking."isCancelled" IS FALSE
         AND offer.type != 'ThingType.ACTIVATION'
         AND offer.type != 'EventType.ACTIVATION'
        GROUP BY offerer.id, offerer.name
        ORDER BY booking_amount DESC, offerer.name ASC
        LIMIT 20;
        """
    return db.engine.execute(query).fetchall()
