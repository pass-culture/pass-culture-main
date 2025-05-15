import pcapi.connectors.big_query.queries as big_queries
from pcapi import settings
from pcapi.core.external.sendinblue import add_contacts_to_list


def pro_no_active_offers_since_40_days_automation() -> bool:
    """
    Send a notification email to pros whose offers are inactive since 40 days ago.

    List: pros-pas-offre-active-40-j
    """
    churned_pro_emails = [row.venue_booking_email for row in big_queries.ChurnedProEmail().execute()]
    return add_contacts_to_list(
        churned_pro_emails,
        settings.SENDINBLUE_PRO_NO_ACTIVE_OFFERS_40_DAYS_ID,
        use_pro_subaccount=True,
    )


def pro_no_bookings_since_40_days_automation() -> bool:
    """
    Send a notification email to pros whose offers haven't been booked since 40 days ago.

    List: pros-pas-de-resa-40-j
    """
    no_bookings_pro_emails = [row.venue_booking_email for row in big_queries.NoBookingsProEmail().execute()]
    return add_contacts_to_list(
        no_bookings_pro_emails,
        settings.SENDINBLUE_PRO_NO_BOOKINGS_40_DAYS_ID,
        use_pro_subaccount=True,
    )


def update_pro_contacts_list_for_live_show_churned_40_days_ago() -> bool:
    emails = [row.venue_booking_email for row in big_queries.ProLiveShowEmailChurned40DaysAgoQuery().execute()]
    return add_contacts_to_list(
        emails,
        settings.SENDINBLUE_PRO_MARKETING_LIVE_SHOW_EMAIL_CHURNED_40_DAYS_AGO,
        use_pro_subaccount=True,
    )


def update_pro_contacts_list_for_live_show_last_booking_40_days_ago() -> bool:
    emails = [row.venue_booking_email for row in big_queries.ProLiveShowEmailLastBooking40DaysAgoQuery().execute()]
    return add_contacts_to_list(
        emails,
        settings.SENDINBLUE_PRO_MARKETING_LIVE_SHOW_EMAIL_LAST_BOOKING_40_DAYS_AGO,
        use_pro_subaccount=True,
    )
