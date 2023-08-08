from pcapi import settings

from .base import BaseQuery
from .base import RowIterator
from .models import ProEmailModel


class NoBookingsProEmail(BaseQuery):
    raw_query = f"""
        select
            distinct venue_booking_email
        from
            `{settings.BIG_QUERY_NOTIFICATIONS_TABLE_BASENAME}.marketing_pro_email_last_booking_40_days_ago`
        where
            cast(execution_date as date) = current_date()
    """

    model = ProEmailModel

    def execute(self, page_size: int = 1_000) -> RowIterator:
        for row in super().execute(page_size):
            yield ProEmailModel(venue_booking_email=row.venue_booking_email)
