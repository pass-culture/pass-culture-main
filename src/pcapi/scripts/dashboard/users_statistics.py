from typing import List
from typing import Tuple

import pandas
from sqlalchemy import func
from sqlalchemy.orm import Query

import pcapi.core.bookings.repository as booking_repository
from pcapi.models import Booking
from pcapi.models import EventType
from pcapi.models import Offer
from pcapi.models import StockSQLEntity
from pcapi.models import ThingType
from pcapi.models import UserSQLEntity
from pcapi.models.db import db
import pcapi.repository.user_queries as user_repository


def count_activated_users(departement_code: str = None) -> int:
    if departement_code is None:
        return user_repository.count_all_activated_users()

    return user_repository.count_all_activated_users_by_departement(departement_code)


def count_users_having_booked(departement_code: str = None) -> int:
    if departement_code is None:
        return user_repository.count_users_having_booked()

    return user_repository.count_users_having_booked_by_departement_code(departement_code)


def get_mean_number_of_bookings_per_user_having_booked(departement_code: str = None) -> float:
    number_of_users_having_booked = count_users_having_booked(departement_code)

    number_of_non_cancelled_bookings = (
        booking_repository.count_non_cancelled()
        if (departement_code is None)
        else booking_repository.count_non_cancelled_by_departement(departement_code)
    )
    if not number_of_users_having_booked:
        return 0

    return number_of_non_cancelled_bookings / number_of_users_having_booked


def get_mean_amount_spent_by_user(departement_code: str = None) -> float:
    number_of_users_having_booked = count_users_having_booked(departement_code)
    amount_spent_on_bookings = _query_amount_spent_by_departement(departement_code).scalar()

    if not amount_spent_on_bookings:
        return 0

    return float(amount_spent_on_bookings / number_of_users_having_booked)


def get_non_cancelled_bookings_by_user_departement() -> pandas.DataFrame:
    non_cancelled_bookings_by_user_departement = _query_get_non_cancelled_bookings_by_user_departement()
    return pandas.DataFrame(
        columns=["Département de l'utilisateur", "Nombre de réservations"],
        data=non_cancelled_bookings_by_user_departement,
    )


def _query_amount_spent_by_departement(departement_code: str) -> Query:
    query = db.session.query(func.sum(Booking.amount * Booking.quantity))

    if departement_code:
        query = query.join(UserSQLEntity).filter(UserSQLEntity.departementCode == departement_code)

    query = (
        query.join(StockSQLEntity, StockSQLEntity.id == Booking.stockId)
        .join(Offer)
        .filter(Offer.type != str(ThingType.ACTIVATION))
        .filter(Offer.type != str(EventType.ACTIVATION))
    )

    return query.filter(Booking.isCancelled == False)


def _query_get_non_cancelled_bookings_by_user_departement() -> List[Tuple[str, int]]:
    return db.engine.execute(
        """
        SELECT "user"."departementCode" as "departementCode", SUM("booking"."quantity") as booking_quantity
        FROM booking
        JOIN "user" ON "user".id = booking."userId"
        JOIN stock ON stock.id = booking."stockId"
        JOIN offer ON offer.id = stock."offerId"
        WHERE booking."isCancelled" IS FALSE
         AND offer.type != 'ThingType.ACTIVATION'
         AND offer.type != 'EventType.ACTIVATION'
        GROUP BY "user"."departementCode"
        ORDER BY booking_quantity DESC ;
        """
    ).fetchall()
