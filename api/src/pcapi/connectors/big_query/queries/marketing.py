import pydantic.v1 as pydantic_v1

from pcapi import settings

from .base import BaseQuery


class ProLiveShowEmailChurned40DaysAgoModel(pydantic_v1.BaseModel):
    venue_booking_email: str


class ProLiveShowEmailChurned40DaysAgoQuery(BaseQuery):
    raw_query = f"""
        select
            distinct venue_booking_email
        from
            `{settings.BIG_QUERY_TABLE_BASENAME}.marketing_pro_live_show_email_churned_40_days_ago`
        where
            cast(execution_date as date) = current_date()
            and venue_booking_email is not null
            and TRIM(venue_booking_email) != ''
    """

    model = ProLiveShowEmailChurned40DaysAgoModel


class ProLiveShowEmailLastBooking40DaysAgoModel(pydantic_v1.BaseModel):
    venue_booking_email: str


class ProLiveShowEmailLastBooking40DaysAgoQuery(BaseQuery):
    raw_query = f"""
        select
            distinct venue_booking_email
        from
            `{settings.BIG_QUERY_TABLE_BASENAME}.marketing_pro_live_show_email_last_booking_40_days_ago`
        where
            cast(execution_date as date) = current_date()
            and venue_booking_email is not null
            and TRIM(venue_booking_email) != ''
    """

    model = ProLiveShowEmailLastBooking40DaysAgoModel
