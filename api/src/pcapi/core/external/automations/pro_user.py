from pcapi import settings
import pcapi.connectors.big_query.queries as big_queries
from pcapi.core.external.sendinblue import add_contacts_to_list
from pcapi.models.feature import FeatureToggle


def pro_no_active_offers_since_40_days_automation() -> bool:
    """
    Send a notification email to pros whose offers are inactive since 40 days ago.

    List: pros-pas-offre-active-40-j
    """
    churned_pro_emails = [row.venue_booking_email for row in big_queries.ChurnedProEmail().execute()]
    return add_contacts_to_list(
        churned_pro_emails,
        (
            settings.SENDINBLUE_PRO_SUBACCOUNT_NO_ACTIVE_OFFERS_40_DAYS_ID
            if FeatureToggle.WIP_ENABLE_BREVO_PRO_SUBACCOUNT.is_active()
            else settings.SENDINBLUE_PRO_NO_ACTIVE_OFFERS_40_DAYS_ID
        ),
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
        (
            settings.SENDINBLUE_PRO_SUBACCOUNT_NO_BOOKINGS_40_DAYS_ID
            if FeatureToggle.WIP_ENABLE_BREVO_PRO_SUBACCOUNT.is_active()
            else settings.SENDINBLUE_PRO_NO_BOOKINGS_40_DAYS_ID
        ),
        use_pro_subaccount=True,
    )
