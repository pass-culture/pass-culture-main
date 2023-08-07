from pcapi import settings
import pcapi.connectors.big_query.queries as big_queries
from pcapi.core.external.sendinblue import add_contacts_to_list


def pro_no_active_offers_since_40_days_automation() -> bool:
    """
    Send a notification email to pros whose offers are inactive since 40 days ago.

    List: pros-pas-offre-active-40-j
    """
    churned_pro_emails = [row.venue_booking_email for row in big_queries.ChurnedProEmail().execute()]
    return add_contacts_to_list(churned_pro_emails, settings.SENDINBLUE_PRO_NO_ACTIVE_OFFERS_40_DAYS_ID)
