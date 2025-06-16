from pcapi import settings

from .base import BaseQuery
from .models import ProEmailModel


class ChurnedProEmail(BaseQuery):
    raw_query = f"""
        select
            distinct venue_booking_email
        from
            `{settings.BIG_QUERY_TABLE_BASENAME}.marketing_pro_email_churned_40_days_ago`
        where
            cast(execution_date as date) = current_date()
            and venue_booking_email is not null
            and TRIM(venue_booking_email) != ''
    """

    model = ProEmailModel
