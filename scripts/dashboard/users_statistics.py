import pandas

from sqlalchemy import func

from models import User, Booking
from models.db import db
import repository.user_queries as user_repository


def count_activated_users():
    return user_repository.count_activated_users()


def count_users_having_booked():
    return User.query.join(Booking).distinct(User.id).count()


def get_mean_number_of_bookings_per_user_having_booked():
    number_of_users_having_booked = count_users_having_booked()

    if not number_of_users_having_booked:
        return 0

    number_of_non_cancelled_bookings = Booking.query.filter_by(isCancelled=False).count()
    return number_of_non_cancelled_bookings / number_of_users_having_booked


def get_mean_amount_spent_by_user():
    number_of_users_having_booked = count_users_having_booked()
    number_of_bookings = db.session.query(func.sum(Booking.amount * Booking.quantity)).filter_by(isCancelled=False).scalar()

    if not number_of_bookings:
        return 0
    return number_of_bookings / number_of_users_having_booked


def get_non_cancelled_bookings_by_user_departement():
    non_cancelled_bookings_by_user_departement = _query_get_non_cancelled_bookings_by_user_departement()
    return pandas.DataFrame(columns=["Département de l\'utilisateur", 'Nombre de réservations'],
                            data=non_cancelled_bookings_by_user_departement)


def _query_get_non_cancelled_bookings_by_user_departement():
    return db.engine.execute(
        """
        SELECT "user"."departementCode" as "departementCode", SUM("booking"."quantity")
        FROM booking
        JOIN "user" ON "user".id = booking."userId"
        WHERE booking."isCancelled" IS FALSE
        GROUP BY "user"."departementCode"
        ORDER BY "user"."departementCode";
        """).fetchall()
