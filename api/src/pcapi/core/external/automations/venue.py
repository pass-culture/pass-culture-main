from collections.abc import Iterable
from datetime import date
from datetime import datetime

from dateutil.relativedelta import relativedelta
import sqlalchemy as sa

from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.external.sendinblue import add_contacts_to_list
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


YIELD_COUNT_PER_DB_QUERY = 1000


def get_inactive_venues_emails() -> Iterable[str]:
    # See request conditions in pro_inactive_venues_automation() below
    ninety_days_ago = datetime.combine(date.today() - relativedelta(days=90), datetime.min.time())

    venue_has_approved_offer_subquery = offers_models.Offer.query.filter(
        offers_models.Offer.venueId == offerers_models.Venue.id,
        offers_models.Offer.isActive.is_(True),
        offers_models.Offer.validation == OfferValidationStatus.APPROVED,
    ).exists()

    venue_has_no_booking_within_the_last_90_days_subquery = sa.not_(
        offers_models.Offer.query.filter(
            offers_models.Offer.venueId == offerers_models.Venue.id,
            offers_models.Offer.isActive.is_(True),
            offers_models.Offer.validation == OfferValidationStatus.APPROVED,
        )
        .join(offers_models.Stock)
        .join(bookings_models.Booking)
        .filter(
            bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
            bookings_models.Booking.dateCreated >= datetime.utcnow() - relativedelta(days=90),
        )
        .exists()
    )

    query = (
        db.session.query(offerers_models.Venue.bookingEmail)
        .join(offerers_models.Offerer)
        .filter(
            offerers_models.Offerer.dateValidated < ninety_days_ago,
            offerers_models.Venue.bookingEmail.is_not(None),
            sa.not_(
                offerers_models.Venue.venueTypeCode.in_(
                    [offerers_models.VenueTypeCode.FESTIVAL, offerers_models.VenueTypeCode.DIGITAL]
                )
            ),
            venue_has_approved_offer_subquery,
            venue_has_no_booking_within_the_last_90_days_subquery,
        )
        .distinct()
        .yield_per(YIELD_COUNT_PER_DB_QUERY)
    )

    return (email for email, in query)


def pro_inactive_venues_automation() -> bool:
    """
    Check venues which have no reservation for a long time (more than 90 days) on their offers and look inactive.

    Conditions:
    - parent offerer has been validated more than 90 days ago
    - venue has a bookingEmail address set
    - venue type is not digital nor festival
    - venue has at least one approved and active individual offer
    - there is no booking made with the last three months among currently active offers

    List: pros-inactivité-90j
    """
    return add_contacts_to_list(get_inactive_venues_emails(), settings.SENDINBLUE_PRO_INACTIVE_90_DAYS_ID)
