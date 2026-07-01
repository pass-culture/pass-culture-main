import pydantic

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery


class Last30DaysBookingsModel(pydantic.BaseModel):
    ean: str
    booking_count: int


class Last30DaysBookings(BaseQuery):
    raw_query = f"""
        SELECT
            isbn as ean,
            nb_booking as booking_count
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.booking_per_ean_last_30_days`
    """

    model = Last30DaysBookingsModel
