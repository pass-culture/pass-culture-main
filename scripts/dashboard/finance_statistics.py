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
        GROUP BY offer.id, offer.name
        ORDER BY quantity DESC, offer.name ASC ;
        """)