from pcapi import settings

from .base import BaseQuery
from .models import ProEmailModel


class NoBookingsProEmail(BaseQuery):
    raw_query = f"""
        select
            distinct venue_booking_email
        from
            `{settings.BIG_QUERY_TABLE_BASENAME}.marketing_pro_email_last_booking_40_days_ago`
        where
            cast(execution_date as date) = current_date()
    """

    model = ProEmailModel
